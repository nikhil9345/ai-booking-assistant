# 🤖 AI Booking Assistant (RAG-Powered)

An AI-driven, chat-based Booking Assistant that supports document-aware question answering (RAG), conversational booking flows, persistent storage, email confirmations, and an admin dashboard — built using **Streamlit**, **FastAPI**, and **SQLite**.

---

## 📌 Features

### 💬 Conversational AI
- Chat-based interface using Streamlit
- Detects **booking intent** vs **general questions**
- Multi-turn conversation with short-term memory
- Explicit confirmation before saving bookings

### 📄 RAG (Retrieval-Augmented Generation)
- Upload one or more PDFs via UI
- Extracts and chunks text
- Generates embeddings and stores them in memory
- Answers user questions using retrieved document context

### 🗓 Conversational Booking Flow
Collects details step-by-step:
- Name
- Email (validated)
- Phone number (validated)
- Booking type (hotel / doctor / salon etc.)
- Preferred date
- Preferred time

Before saving:
- Summarizes details
- Asks explicit **Confirm / Cancel**

### 🗄 Data Persistence
- SQLite database
- Auto-generated booking IDs
- Persistent storage across sessions

### 📧 Email Confirmation
- Sends confirmation email after successful booking
- Gracefully handles email failures without blocking booking

### 🛠 Admin Dashboard
- View all stored bookings
- Search and filter by:
  - Name
  - Email
  - Date

---

## 🧠 System Architecture

Streamlit (Frontend UI)
|
| HTTP
v
FastAPI Backend
├─ Intent Detection
├─ Booking Flow Logic
├─ RAG Pipeline
├─ SQLite Persistence
└─ Email Service

---

## 📂 Project Structure

AI_UseCase/
│
├── app.py # Streamlit frontend
├── backend_api.py # FastAPI backend
│
├── booking_flow.py # Booking intent & slot filling
├── models/
│ ├── embeddings.py # Vector embeddings
│ └── llm.py # LLM abstraction
│
├── db/
│ └── database.py # SQLite logic
│
├── utils/
│ └── email_service.py # Email confirmation
│
├── docs/ # Sample PDFs & diagrams
│
├── requirements.txt
├── README.md
└── .streamlit/
└── secrets.toml

---

## ⚙️ Setup Instructions (Local)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/nikhil9345/ai-booking-assistant.git
cd ai-booking-assistant
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash pip install -r requirements.txt ```

### 🔑 Environment Configuration
```bash
Create .streamlit/secrets.toml:

EMAIL_SENDER="dummy@gmail.com"
EMAIL_PASSWORD="dummy_app_password"
```

⚠️ Email credentials are optional.
Booking works even if email delivery fails.

### ▶️ Running the Application
Start Backend
```bash
uvicorn backend_api:app --reload
```
Start Frontend
```bash
streamlit run app.py
```
Open browser:
```bash
http://localhost:8501
```

### 🧪 How to Test
-📄 RAG Test
-Upload a real PDF
-Ask:
-What is the check-in time?
-✔ Answer should come from the PDF
-🗓 Booking Test
-I want to book an appointment
-Follow prompts → Confirm booking
-✔ Booking ID generated
-✔ Saved in database
-✔ Email attempted

### 🛠 Admin Dashboard
-Switch to Admin Dashboard
-Verify booking appears in table

### ⚠️ Error Handling
-Invalid email / phone / date inputs
-Invalid or empty PDFs
-Database connection issues
-Email delivery failures
-Graceful user-friendly error messages

### 🔮 Future Improvements
-User booking lookup by email
-Cancel / reschedule bookings
-Persistent vector store (FAISS / Chroma)
-Voice input/output (STT/TTS)
-Authentication for Admin Dashboard

### 📌 Notes
-SQLite persistence is acceptable for this assignment
-In-memory vector store used for simplicity
-System is designed for clarity, robustness, and evaluation readiness

### 👤 Author
-Atchuta Nikhil Suhaas
-AI Engineer Assignment – NeoStats

