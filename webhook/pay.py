"""Razorpay webhook: payment captured -> find which course -> email the Drive link.

NOTHING secret lives in this file. Configure these environment variables on your host:
  RZP_WEBHOOK_SECRET   the secret you typed into Razorpay's webhook settings
  MAIL_USER            Gmail address that sends the emails
  MAIL_APP_PASSWORD    Gmail App Password (only for hosts that allow SMTP)
  RESEND_API_KEY       Resend API key (HTTPS; needs a verified domain to email customers)
  MAIL_FROM            e.g. Analyst Shubhi <onboarding@resend.dev> (testing) or hello@yourdomain.com
  APPS_SCRIPT_URL      Google Apps Script web-app URL that sends the mail (use on Render free: SMTP is blocked)
  APPS_SCRIPT_TOKEN    shared secret the script checks before sending
  PRODUCTS_JSON        JSON list of courses, e.g.
    [{"title":"PL SQL Project Guide",
      "ids":["pl_XXXXXXXX","plink_XXXXXXXX"],
      "amount":4900,
      "url":"https://drive.google.com/..."}]
    ids    = Razorpay payment page / payment link ids for that course
    amount = price in PAISE (₹49 = 4900), only used as a fallback match
Start:  uvicorn pay:app --host 0.0.0.0 --port $PORT
"""
import hashlib
import hmac
import json
import os
import smtplib
import sqlite3
import urllib.error
import urllib.request
from email.message import EmailMessage

from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


def load_products():
    raw = os.getenv("PRODUCTS_JSON")
    if not raw:
        raise RuntimeError("PRODUCTS_JSON environment variable is not set")
    return json.loads(raw)


PRODUCTS = load_products()
DB = os.getenv("DB_PATH", "payments.db")


def seen(payment_id: str) -> bool:
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS done (payment_id TEXT PRIMARY KEY, email TEXT, product TEXT, ts DEFAULT CURRENT_TIMESTAMP)")
        return c.execute("SELECT 1 FROM done WHERE payment_id=?", (payment_id,)).fetchone() is not None


def mark(payment_id: str, email: str, product: str):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT OR IGNORE INTO done (payment_id, email, product) VALUES (?,?,?)", (payment_id, email, product))


def find_product(raw_text: str, amount: int):
    for p in PRODUCTS:                       # 1) any known id appearing in the payload
        if any(i in raw_text for i in p["ids"]):
            return p, "id"
    same = [p for p in PRODUCTS if p.get("amount") == amount]
    if len(same) == 1:                       # 2) fallback: exactly one course with this price
        return same[0], "amount"
    return None, None


def send_mail(to: str, name: str, title: str, url: str):
    first = (name or "there").split()[0]
    body = (f"Hi {first},\n\nThank you for your payment! 🎉\n\n"
            f"Here is your access to “{title}”:\n{url}\n\n"
            f"Tip: open the link while logged in to Google and save a copy to your Drive.\n"
            f"If it doesn’t open, just reply to this email and I’ll sort it out.\n\n"
            f"All the best,\nShubhanshi\nAnalyst Shubhi")
    api_key = os.getenv("RESEND_API_KEY")
    if api_key:  # HTTPS (port 443): works on Render free, where SMTP ports are blocked
        payload = json.dumps({"from": os.environ["MAIL_FROM"], "to": [to],
                              "subject": f"Your purchase: {title}", "text": body}).encode()
        r = urllib.request.Request("https://api.resend.com/emails", data=payload, method="POST", headers={
            "Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
            "User-Agent": "analyst-shubhi-webhook/1.0"})
        try:
            with urllib.request.urlopen(r, timeout=15) as resp:
                print(f"[mail] sent via Resend to {to} (status {resp.status})")
        except urllib.error.HTTPError as err:
            print(f"[mail] Resend error {err.code}: {err.read().decode()[:300]}")
            raise  # -> 500 -> Razorpay retries
        return

    script_url = os.getenv("APPS_SCRIPT_URL")
    if script_url:  # HTTPS (port 443) -> Google Apps Script -> sends from your Gmail. Works on Render free.
        payload = json.dumps({"token": os.environ["APPS_SCRIPT_TOKEN"], "to": to,
                              "subject": f"Your purchase: {title}", "body": body}).encode()
        r = urllib.request.Request(script_url, data=payload, method="POST",
                                   headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=30) as resp:  # follows Google's redirect automatically
            out = resp.read().decode().strip()
        if out != "ok":
            print(f"[mail] Apps Script replied: {out[:200]}")
            raise RuntimeError("Apps Script did not confirm the send")  # -> 500 -> Razorpay retries
        print(f"[mail] sent via Gmail (Apps Script) to {to}")
        return

    user, pwd = os.getenv("MAIL_USER"), os.getenv("MAIL_APP_PASSWORD")
    if not (user and pwd):
        print(f"[DRY RUN] would email {to} for {title}")
        return
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = f"Your purchase: {title}", f"Analyst Shubhi <{user}>", to
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pwd)
        s.send_message(msg)
    print(f"[mail] sent to {to}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/razorpay-webhook")
async def razorpay_webhook(req: Request):
    raw = await req.body()
    sig = req.headers.get("x-razorpay-signature", "")
    expected = hmac.new(os.environ["RZP_WEBHOOK_SECRET"].encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise HTTPException(400, "Invalid signature")

    data = json.loads(raw)
    event = data.get("event")
    print(f"[webhook] event={event}")

    if event in ("payment.captured", "payment_link.paid"):
        pay = data["payload"]["payment"]["entity"]
        notes = pay.get("notes") or {}
        email = pay.get("email") or notes.get("email")
        name = notes.get("name", "")
        pid, amount = pay["id"], pay["amount"]

        product, how = find_product(raw.decode(), amount)
        print(f"[webhook] payment={pid} amount={amount / 100} matched={product['title'] if product else None} by={how}")

        if not product:
            print("[webhook] NO MATCH - check ids/amount in PRODUCTS_JSON")  # no payload dump: keeps buyer data out of logs
        elif not email:
            print("[webhook] no buyer email on payment")
        elif seen(pid):
            print(f"[webhook] duplicate {pid}, skipping")
        else:
            send_mail(email, name, product["title"], product["url"])  # error -> 500 -> Razorpay retries
            mark(pid, email, product["title"])
    return {"ok": True}
