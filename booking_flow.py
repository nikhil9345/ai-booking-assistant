import re
from datetime import datetime

FIELDS = ["name","email","phone","booking_type","date","time"]

def detect_booking_intent(text):
    return any(w in text.lower() for w in
        ["book","booking","appointment","reserve"])

def next_field(data):
    for f in FIELDS:
        if f not in data:
            return f
    return None

def prompt_for(field):
    return {
        "name": "Please tell me your full name.",
        "email": "Please provide your email address.",
        "phone": "Please provide your 10-digit phone number.",
        "booking_type": "What type of booking do you want?",
        "date": "Enter date (YYYY-MM-DD).",
        "time": "Enter time (HH:MM)."
    }[field]

def validate(field, val):
    try:
        if field=="email":
            return re.match(r"[^@]+@[^@]+\.[^@]+",val)
        if field=="phone":
            return val.isdigit() and len(val)==10
        if field=="date":
            datetime.strptime(val,"%Y-%m-%d")
        if field=="time":
            datetime.strptime(val,"%H:%M")
        return True
    except:
        return False

def summarize(d):
    return (
        f"Please confirm:\n\n"
        f"Name: {d['name']}\n"
        f"Email: {d['email']}\n"
        f"Phone: {d['phone']}\n"
        f"Type: {d['booking_type']}\n"
        f"Date: {d['date']}\n"
        f"Time: {d['time']}\n\n"
        f"Reply Confirm or Cancel."
    )
