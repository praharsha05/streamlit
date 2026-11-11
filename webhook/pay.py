"""Razorpay webhook relay.

Verifies Razorpay's signature (Apps Script can't read request headers) and passes the paid
payment on to the Google Apps Script back office, which looks up the course, sends the email,
books the call and logs the sale.

Environment variables (Render -> Environment):
  RZP_WEBHOOK_SECRET   secret typed into Razorpay's webhook settings
  APPS_SCRIPT_URL      Apps Script web-app URL (ends in /exec)
  APPS_SCRIPT_TOKEN    must equal the script property TOKEN

Start:  uvicorn pay:app --host 0.0.0.0 --port $PORT
Razorpay webhook event to tick: payment_link.paid
"""
import hashlib
import hmac
import json
import os
import urllib.request

from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


def call_script(payload: dict) -> dict:
    req = urllib.request.Request(os.environ["APPS_SCRIPT_URL"], data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:   # follows Google's redirect automatically
        return json.loads(resp.read().decode())


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

    if event == "payment_link.paid":
        link = data["payload"]["payment_link"]["entity"]
        pay = data["payload"]["payment"]["entity"]
        result = call_script({
            "token": os.environ["APPS_SCRIPT_TOKEN"],
            "action": "fulfil",
            "payment_id": pay["id"],
            "payment_link_id": link["id"],
            "amount": pay["amount"],                                   # paise
            "email": pay.get("email"),
            "customer_email": (link.get("customer") or {}).get("email"),
            "notes": link.get("notes") or {},
        })
        print(f"[webhook] payment={pay['id']} course={(link.get('notes') or {}).get('course_id')} -> {result}")
        if not result.get("ok"):
            raise HTTPException(500, "Back office did not confirm")   # Razorpay will retry
    return {"ok": True}
