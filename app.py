import streamlit as st
from pypdf import PdfReader
from db.database import init_db, save_booking, get_all_bookings
from booking_flow import *
from rag_pipeline import *

init_db()

st.set_page_config("AI Booking Assistant","🤖","wide")

if "messages" not in st.session_state:
    st.session_state.messages=[]
if "pdf_chunks" not in st.session_state:
    st.session_state.pdf_chunks=[]
    st.session_state.pdf_embeddings=[]
if "booking" not in st.session_state:
    st.session_state.booking={"active":False,"data":{}}

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to",["Chat","Admin Dashboard"])

if page=="Chat":
    st.title("🤖 AI Booking Assistant")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    pdf = st.file_uploader("Upload PDF",type=["pdf"])
    if pdf:
        reader=PdfReader(pdf)
        text="".join(p.extract_text() or "" for p in reader.pages)
        if text.strip():
            chunks=chunk_text(text)
            st.session_state.pdf_chunks=chunks
            st.session_state.pdf_embeddings=embed_chunks(chunks)
            extracted=extract_fields_from_text(text)
            st.session_state.booking["data"].update(extracted)
            st.success("PDF processed")
        else:
            st.error("No readable text")

    if prompt:=st.chat_input("Ask or book"):
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)

        reply=""
        b=st.session_state.booking

        if b["active"]:
            if prompt.lower()=="cancel":
                st.session_state.booking={"active":False,"data":{}}
                reply="Booking cancelled."
            elif prompt.lower()=="confirm":
                bid=save_booking(b["data"])
                st.session_state.booking={"active":False,"data":{}}
                reply=f"Booking confirmed. ID: {bid}"
            else:
                f=next_field(b["data"])
                if not validate(f,prompt):
                    reply=prompt_for(f)
                else:
                    b["data"][f]=prompt
                    nf=next_field(b["data"])
                    reply=prompt_for(nf) if nf else summarize(b["data"])

        elif detect_booking_intent(prompt):
            st.session_state.booking["active"]=True
            f=next_field(st.session_state.booking["data"])
            reply=prompt_for(f)

        elif st.session_state.pdf_chunks:
            reply=rag_answer(prompt,
                st.session_state.pdf_chunks,
                st.session_state.pdf_embeddings)
        else:
            reply="I do not know."

        st.session_state.messages.append({"role":"assistant","content":reply})
        with st.chat_message("assistant"): st.markdown(reply)

if page=="Admin Dashboard":
    st.title("🛠 Admin Dashboard")
    rows=get_all_bookings()
    if rows:
        st.dataframe([{
            "Booking ID":r[0],"Name":r[1],"Email":r[2],
            "Phone":r[3],"Type":r[4],"Date":r[5],
            "Time":r[6],"Status":r[7],"Created":r[8]
        } for r in rows])
    else:
        st.info("No bookings yet.")
