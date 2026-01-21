import streamlit as st
import sqlite3
import re
from datetime import datetime
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Booking Assistant",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# DATABASE (SQLite)
# -----------------------------
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
    booking_id = cur.lastrowid
    conn.close()
    return booking_id

def fetch_bookings():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

init_db()

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_chunks" not in st.session_state:
    st.session_state.pdf_chunks = []
    st.session_state.pdf_embeddings = []

if "booking_state" not in st.session_state:
    st.session_state.booking_state = {
        "active": False,
        "data": {},
        "current_field": None
    }

# -----------------------------
# MODELS
# -----------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

REQUIRED_FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

# -----------------------------
# UTILS
# -----------------------------
def detect_booking_intent(text):
    keywords = ["book", "appointment", "reservation", "schedule"]
    return any(k in text.lower() for k in keywords)

def field_prompt(field):
    prompts = {
        "name": "Please tell me your full name.",
        "email": "Please provide your email address.",
        "phone": "Please provide your 10-digit phone number.",
        "booking_type": "What type of booking do you want? (hotel / doctor / salon etc.)",
        "date": "Please enter the preferred date (YYYY-MM-DD).",
        "time": "Please enter the preferred time (HH:MM)."
    }
    return prompts[field]

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

def summarize_booking(data):
    return (
        f"Please confirm your booking details:\n\n"
        f"Name: {data['name']}\n"
        f"Email: {data['email']}\n"
        f"Phone: {data['phone']}\n"
        f"Booking Type: {data['booking_type']}\n"
        f"Date: {data['date']}\n"
        f"Time: {data['time']}\n\n"
        f"Reply with **Confirm** to proceed or **Cancel** to stop."
    )

def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Chat", "Admin Dashboard"])

# =============================
# CHAT PAGE
# =============================
if page == "Chat":
    st.title("🤖 AI Booking Assistant")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # PDF Upload (RAG)
    st.subheader("📄 Upload PDF for Q&A")
    pdf = st.file_uploader("Upload a PDF", type=["pdf"])

    if pdf:
        reader = PdfReader(pdf)
        text = "".join(page.extract_text() or "" for page in reader.pages)

        if text.strip():
            chunks = chunk_text(text)
            embeddings = embedder.encode(chunks)

            st.session_state.pdf_chunks.extend(chunks)
            st.session_state.pdf_embeddings.extend(embeddings)

            st.success("PDF uploaded and indexed successfully")
        else:
            st.error("PDF has no readable text")

    # Chat input
    if prompt := st.chat_input("Ask a question or start a booking..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        reply = ""

        booking = st.session_state.booking_state

        # ------------------ BOOKING FLOW ------------------
        if booking["active"]:

            lower = prompt.lower()

            if lower == "cancel":
                st.session_state.booking_state = {"active": False, "data": {}, "current_field": None}
                reply = "❌ Booking cancelled."

            elif lower == "confirm":
                missing = [f for f in REQUIRED_FIELDS if f not in booking["data"]]
                if missing:
                    booking["current_field"] = missing[0]
                    reply = field_prompt(missing[0])
                else:
                    booking_id = save_booking(booking["data"])
                    st.session_state.booking_state = {"active": False, "data": {}, "current_field": None}
                    reply = f"✅ Booking confirmed! ID: {booking_id}."

            else:
                field = booking["current_field"]
                if not validate_field(field, prompt):
                    reply = f"Invalid {field}. {field_prompt(field)}"
                else:
                    booking["data"][field] = prompt
                    booking["current_field"] = next_missing_field(booking["data"])
                    if booking["current_field"]:
                        reply = field_prompt(booking["current_field"])
                    else:
                        reply = summarize_booking(booking["data"])

        # ------------------ START BOOKING ------------------
        elif detect_booking_intent(prompt):
            st.session_state.booking_state = {
                "active": True,
                "data": {},
                "current_field": "name"
            }
            reply = field_prompt("name")

        # ------------------ RAG ------------------
        elif st.session_state.pdf_chunks:
            query_emb = embedder.encode([prompt])[0]
            sims = cosine_similarity(
                [query_emb],
                st.session_state.pdf_embeddings
            )[0]
            reply = st.session_state.pdf_chunks[sims.argmax()]

        else:
            reply = "I do not know."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

# =============================
# ADMIN DASHBOARD
# =============================
if page == "Admin Dashboard":
    st.title("🛠 Admin Dashboard")

    rows = fetch_bookings()
    if rows:
        st.dataframe(
            [
                {
                    "Booking ID": r[0],
                    "Name": r[1],
                    "Email": r[2],
                    "Phone": r[3],
                    "Type": r[4],
                    "Date": r[5],
                    "Time": r[6],
                    "Status": r[7],
                    "Created At": r[8],
                }
                for r in rows
            ],
            width="stretch"
        )
    else:
        st.info("No bookings yet.")
