import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="AI Booking Assistant", layout="wide")

BACKEND_URL = "http://127.0.0.1:8000"

def fetch_bookings():
    response = requests.get("http://127.0.0.1:8000/admin/bookings")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()


st.sidebar.title("Navigation")
mode = st.sidebar.radio("Select Mode", ["User Chat", "Admin Dashboard"])

if mode == "User Chat":
    st.title("🤖 AI Booking Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about your booking...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"message": user_input},
                timeout=15
            )

            if response.status_code == 200:
                bot_response = response.json()["reply"]
            else:
                bot_response = "Backend error"

        except requests.exceptions.RequestException:
            bot_response = "Backend not running"

        st.session_state.messages.append(
            {"role": "assistant", "content": bot_response}
        )
        with st.chat_message("assistant"):
            st.markdown(bot_response)

    st.divider()

    st.subheader("📄 Upload Booking PDF")

    uploaded_pdf = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"]
    )

    if uploaded_pdf:
        with st.spinner("Uploading and processing PDF..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/upload_pdf",
                    files={"file": uploaded_pdf},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    if data["status"] == "success":
                        st.success("PDF uploaded successfully")
                        st.info("Status: Saved to database")
                        st.info("Status: Confirmation email sent")
                    else:
                        st.error(data["message"])
                else:
                    st.error("Backend error while processing PDF")

            except requests.exceptions.RequestException:
                st.error("Backend not running")

if mode == "Admin Dashboard":
    st.title("🛠 Admin Dashboard")

    st.subheader("All Bookings")
    bookings_df = fetch_bookings()

    col1, col2, col3 = st.columns(3)

    with col1:
        name_filter = st.text_input("Filter by Name")

    with col2:
        email_filter = st.text_input("Filter by Email")

    with col3:
        date_filter = st.text_input("Filter by Date (YYYY-MM-DD)")

    filtered_df = bookings_df.copy()

    if name_filter:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(name_filter, case=False)
        ]

    if email_filter:
        filtered_df = filtered_df[
            filtered_df["email"].str.contains(email_filter, case=False)
        ]

    if date_filter:
        filtered_df = filtered_df[
            filtered_df["date"].str.contains(date_filter)
        ]

    st.dataframe(filtered_df, width="stretch")
