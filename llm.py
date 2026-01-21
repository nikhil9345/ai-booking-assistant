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

def llm_answer(query: str, context: str) -> str:
    llm = get_llm()

    system = """
    You are an AI booking assistant.
    Answer ONLY using the provided context.
    If the answer is not present, say "I do not know."
    """

    messages = [
        SystemMessage(content=system),
        HumanMessage(content=f"Question:\n{query}\n\nContext:\n{context}")
    ]

    response = llm.invoke(messages)
    return response.content.strip()
