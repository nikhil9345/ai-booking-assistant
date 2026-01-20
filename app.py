import streamlit as st
import requests

st.set_page_config(
    page_title="AI Booking Assistant",
    page_icon="🤖",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"

with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to:", ["Chat", "Admin Dashboard"])

if page == "Chat":
    st.title("🤖 AI Booking Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.subheader("📄 Upload PDF for Q&A")
    pdf = st.file_uploader("Upload a PDF", type=["pdf"])

    if pdf:
        with st.spinner("Uploading PDF..."):
            response = requests.post(
                f"{BACKEND_URL}/upload_pdf",
                files={"file": pdf}
            )
            if response.status_code == 200:
                st.success("PDF uploaded and indexed successfully")
            else:
                st.error("PDF upload failed")

    if prompt := st.chat_input("Ask a question or start a booking..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"message": prompt}
                )
                reply = response.json().get("reply", "Error")
                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
if page == "Admin Dashboard":
    st.title("🛠 Admin Dashboard")

    response = requests.get(f"{BACKEND_URL}/admin/bookings")
    if response.status_code == 200:
        st.dataframe(response.json(), use_container_width=True)
    else:
        st.error("Failed to load bookings")
