import streamlit as st
from db.database import get_all_bookings

def render_admin():
    st.title("🛠 Admin Dashboard")
    rows = get_all_bookings()

    if not rows:
        st.info("No bookings yet.")
        return

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
    } for r in rows], use_container_width=True)
