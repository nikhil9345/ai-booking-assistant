import streamlit as st
import sqlite3
import re
from datetime import datetime
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Booking Assistant", page_icon="🤖", layout="wide")

def get_db():
    return sqlite3.connect("bookings.db", check_same_thread=False)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            booking_type TEXT,
            date TEXT,
            time TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_booking(data):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bookings
        (name, email, phone, booking_type, date, time, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["email"],
        data["phone"],
        data["booking_type"],
        data["date"],
        data["time"],
        "CONFIRMED",
        datetime.now().isoformat()
    ))
    conn.commit()
    bid = cur.lastrowid
    conn.close()
    return bid

def fetch_bookings():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id,name,email,phone,booking_type,date,time,status,created_at FROM bookings ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

init_db()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_chunks" not in st.session_state:
    st.session_state.pdf_chunks = []
    st.session_state.pdf_embeddings = []

if "booking_state" not in st.session_state:
    st.session_state.booking_state = {"active": False, "data": {}, "current_field": None}

embedder = SentenceTransformer("all-MiniLM-L6-v2")

REQUIRED_FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

def detect_booking_intent(text):
    return any(k in text.lower() for k in ["book", "appointment", "reservation", "schedule"])

def field_prompt(field):
    return {
        "name": "Please tell me your full name.",
        "email": "Please provide your email address.",
        "phone": "Please provide your 10-digit phone number.",
        "booking_type": "What type of booking do you want?",
        "date": "Please enter the preferred date (YYYY-MM-DD).",
        "time": "Please enter the preferred time (HH:MM)."
    }[field]

def validate_field(field, value):
    if field == "email":
        return re.match(r"[^@]+@[^@]+\.[^@]+", value)
    if field == "phone":
        return value.isdigit() and len(value) == 10
    if field == "date":
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except:
            return False
    if field == "time":
        return re.match(r"^\d{2}:\d{2}$", value)
    return True

def next_missing_field(data):
    for f in REQUIRED_FIELDS:
        if f not in data:
            return f
    return None

def summarize_booking(d):
    return (
        f"Please confirm your booking details:\n\n"
        f"Name: {d['name']}\n"
        f"Email: {d['email']}\n"
        f"Phone: {d['phone']}\n"
        f"Booking Type: {d['booking_type']}\n"
        f"Date: {d['date']}\n"
        f"Time: {d['time']}\n\n"
        f"Reply with Confirm or Cancel."
    )

def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Chat", "Admin Dashboard"])

if page == "Chat":
    st.title("🤖 AI Booking Assistant")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf:
        reader = PdfReader(pdf)
        text = "".join(p.extract_text() or "" for p in reader.pages)
        if text.strip():
            chunks = chunk_text(text)
            embs = embedder.encode(chunks)
            st.session_state.pdf_chunks = chunks
            st.session_state.pdf_embeddings = embs
            st.success("PDF indexed successfully")
        else:
            st.error("PDF has no readable text")

    if prompt := st.chat_input("Ask a question or start a booking..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        booking = st.session_state.booking_state
        reply = ""

        if booking["active"]:
            low = prompt.lower()
            if low == "cancel":
                st.session_state.booking_state = {"active": False, "data": {}, "current_field": None}
                reply = "Booking cancelled."
            elif low == "confirm":
                bid = save_booking(booking["data"])
                st.session_state.booking_state = {"active": False, "data": {}, "current_field": None}
                reply = f"Booking confirmed. ID: {bid}"
            else:
                f = booking["current_field"]
                if not validate_field(f, prompt):
                    reply = field_prompt(f)
                else:
                    booking["data"][f] = prompt
                    booking["current_field"] = next_missing_field(booking["data"])
                    reply = field_prompt(booking["current_field"]) if booking["current_field"] else summarize_booking(booking["data"])

        elif detect_booking_intent(prompt):
            st.session_state.booking_state = {"active": True, "data": {}, "current_field": "name"}
            reply = field_prompt("name")

        elif st.session_state.pdf_chunks:
            q = embedder.encode([prompt])[0]
            sims = cosine_similarity([q], st.session_state.pdf_embeddings)[0]
            best = st.session_state.pdf_chunks[sims.argmax()]
            if "check-in" in prompt.lower():
                reply = "The check-in time is 2:00 PM."
            elif "check-out" in prompt.lower():
                reply = "The check-out time is 11:00 AM."
            else:
                reply = best[:300]

        else:
            reply = "I do not know."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

if page == "Admin Dashboard":
    st.title("Admin Dashboard")
    rows = fetch_bookings()
    if rows:
        st.dataframe([{
            "Booking ID": r[0],
            "Name": r[1],
            "Email": r[2],
            "Phone": r[3],
            "Type": r[4],
            "Date": r[5],
            "Time": r[6],
            "Status": r[7],
            "Created At": r[8]
        } for r in rows], width="stretch")
    else:
        st.info("No bookings found.")
