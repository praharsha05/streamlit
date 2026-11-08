"""Razorpay webhook: payment captured -> find which course -> email the Drive link.

NOTHING secret lives in this file. Configure these environment variables on your host:
  RZP_WEBHOOK_SECRET   the secret you typed into Razorpay's webhook settings
  MAIL_USER            Gmail address that sends the emails
  MAIL_APP_PASSWORD    Gmail App Password (16 characters)
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
