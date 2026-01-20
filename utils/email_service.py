import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_confirmation_email(
    to_email: str,
    name: str,
    booking_id: int,
    booking_type: str,
    date: str,
    time: str
):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        raise RuntimeError("Email credentials not configured")

    subject = f"Booking Confirmation – ID {booking_id}"

    body = f"""
Hi {name},

Your booking has been confirmed successfully.

Booking ID: {booking_id}
Booking Type: {booking_type}
Date: {date}
Time: {time}

Thank you for using our booking assistant.

Regards,
AI Booking Assistant
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
