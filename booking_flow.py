import re
from datetime import datetime

REQUIRED_FIELDS = [
    "name",
    "email",
    "phone",
    "booking_type",
    "date",
    "time"
]

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"


def detect_intent(message: str) -> str:
    booking_keywords = [
        "book", "booking", "appointment", "schedule",
        "reserve", "reservation"
    ]

    message_lower = message.lower()
    for word in booking_keywords:
        if word in message_lower:
            return "booking"

    return "general"


def extract_fields(message: str) -> dict:
    extracted = {}

    email_match = re.search(EMAIL_REGEX, message)
    if email_match:
        extracted["email"] = email_match.group()

    phone_match = re.search(r"\b\d{10}\b", message)
    if phone_match:
        extracted["phone"] = phone_match.group()

    return extracted


def next_missing_field(state: dict):
    for field in REQUIRED_FIELDS:
        if field not in state:
            return field
    return None


def field_prompt(field: str) -> str:
    prompts = {
        "name": "Please tell me your full name.",
        "email": "Please provide your email address.",
        "phone": "Please provide your 10-digit phone number.",
        "booking_type": "What type of booking would you like? (hotel / doctor / salon / etc.)",
        "date": "Please enter the booking date (YYYY-MM-DD).",
        "time": "Please enter the preferred time (HH:MM)."
    }
    return prompts[field]


def validate_field(field: str, value: str) -> bool:
    try:
        if field == "email":
            return re.match(EMAIL_REGEX, value) is not None
        if field == "phone":
            return value.isdigit() and len(value) == 10
        if field == "date":
            datetime.strptime(value, "%Y-%m-%d")
        if field == "time":
            datetime.strptime(value, "%H:%M")
        return True
    except Exception:
        return False


def summarize_booking(state: dict) -> str:
    return (
        f"Please confirm your booking details:\n\n"
        f"Name: {state['name']}\n"
        f"Email: {state['email']}\n"
        f"Phone: {state['phone']}\n"
        f"Booking Type: {state['booking_type']}\n"
        f"Date: {state['date']}\n"
        f"Time: {state['time']}\n\n"
        "Reply with **Confirm** to proceed or **Cancel** to stop."
    )
