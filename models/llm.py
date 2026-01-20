import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.2
    )


def generate_answer(user_query: str, bookings: list) -> str:
    if not bookings:
        return "I could not find any matching bookings."

    llm = get_llm()

    system_prompt = """
    You are an AI booking assistant.
    Answer ONLY using the booking data provided.
    If the answer is not present, say you do not know.
    Do NOT guess or fabricate information.
    """

    context = "\n".join([str(b) for b in bookings])

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
User query:
{user_query}

Booking data:
{context}
""")
    ]

    response = llm.invoke(messages)
    return response.content.strip()
