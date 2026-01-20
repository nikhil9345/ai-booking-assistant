from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from pypdf import PdfReader
import numpy as np

from db.database import init_db, save_booking, get_all_bookings
from utils.email_service import send_confirmation_email

from models.embeddings import get_embedding
from models.llm import generate_answer
from booking_flow import (
    detect_intent,
    next_missing_field,
    field_prompt,
    validate_field,
    summarize_booking
)

app = FastAPI()
init_db()

REQUIRED_FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

BOOKING_STATE = {
    "active": False,
    "data": {},
    "current_field": None
}

PDF_CHUNKS = []
PDF_EMBEDDINGS = []

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


def chunk_text(text, chunk_size=400):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

def search_pdf(query_embedding, top_k=3):
    if not PDF_EMBEDDINGS:
        return []

    scores = [
        float(np.dot(query_embedding, emb))
        for emb in PDF_EMBEDDINGS
    ]

    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [PDF_CHUNKS[i] for i in top_indices]

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    user_message = request.message.strip()
    user_lower = user_message.lower()

    
    if BOOKING_STATE["active"]:

        if user_lower == "confirm":
            booking_data = BOOKING_STATE["data"]

            missing = [f for f in REQUIRED_FIELDS if f not in booking_data]
            if missing:
                BOOKING_STATE["current_field"] = missing[0]
                return ChatResponse(
                    reply=f"Missing {missing[0]}. {field_prompt(missing[0])}"
                )

            booking_id = save_booking(booking_data)

            try:
                send_confirmation_email(
                    to_email=booking_data["email"],
                    name=booking_data["name"],
                    booking_id=booking_id,
                    booking_type=booking_data["booking_type"],
                    date=booking_data["date"],
                    time=booking_data["time"]
                )
                email_msg = "Confirmation email sent."
            except Exception:
                email_msg = "Email could not be sent, but booking was saved."

            BOOKING_STATE["active"] = False
            BOOKING_STATE["data"] = {}
            BOOKING_STATE["current_field"] = None

            return ChatResponse(
                reply=f"✅ Booking confirmed! ID: {booking_id}. {email_msg}"
            )

        if user_lower == "cancel":
            BOOKING_STATE["active"] = False
            BOOKING_STATE["data"] = {}
            BOOKING_STATE["current_field"] = None
            return ChatResponse(reply="❌ Booking cancelled.")

        field = BOOKING_STATE["current_field"]

        if field:
            if not validate_field(field, user_message):
                return ChatResponse(
                    reply=f"Invalid {field}. {field_prompt(field)}"
                )

            BOOKING_STATE["data"][field] = user_message
            BOOKING_STATE["current_field"] = next_missing_field(
                BOOKING_STATE["data"]
            )

            if BOOKING_STATE["current_field"]:
                return ChatResponse(
                    reply=field_prompt(BOOKING_STATE["current_field"])
                )

        return ChatResponse(
            reply=summarize_booking(BOOKING_STATE["data"])
        )

    if detect_intent(user_message) == "booking":
        BOOKING_STATE["active"] = True
        BOOKING_STATE["data"] = {}
        BOOKING_STATE["current_field"] = "name"
        return ChatResponse(reply=field_prompt("name"))

    query_embedding = get_embedding(user_message)
    retrieved_chunks = search_pdf(query_embedding)

    if not retrieved_chunks:
        return ChatResponse(
            reply="I do not know based on the uploaded documents."
        )

    answer = generate_answer(user_message, retrieved_chunks)
    return ChatResponse(reply=answer)

@app.post("/upload_pdf")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"status": "error", "message": "Only PDF files allowed"}

    try:
        reader = PdfReader(file.file)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        if not text.strip():
            return {"status": "error", "message": "PDF has no readable text"}

        chunks = chunk_text(text)

        for chunk in chunks:
            emb = get_embedding(chunk)
            PDF_CHUNKS.append(chunk)
            PDF_EMBEDDINGS.append(emb)

        return {
            "status": "success",
            "chunks_indexed": len(chunks),
            "message": "PDF uploaded and indexed successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/admin/bookings")
def admin_bookings():
    rows = get_all_bookings()

    results = []
    for r in rows:
        results.append({
            "booking_id": r[0],
            "name": r[1],
            "email": r[2],
            "phone": r[3],
            "booking_type": r[4],
            "date": r[5],
            "time": r[6],
            "status": r[7],
            "created_at": r[8],
        })

    return results
