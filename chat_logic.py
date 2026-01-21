from booking_flow import *
from rag_pipeline import retrieve_chunks
from llm import generate_llm_answer
from db.database import save_booking

def handle_chat(prompt, state, rag_store):
    if state["active"]:
        if prompt.lower() == "cancel":
            state["active"] = False
            state["data"] = {}
            return "Booking cancelled."

        if prompt.lower() == "confirm":
            bid = save_booking(state["data"])
            state["active"] = False
            state["data"] = {}
            return f"Booking confirmed. ID: {bid}"

        field = state["current"]
        if not validate_field(field, prompt):
            return prompt_for(field)

        state["data"][field] = prompt
        state["current"] = next_missing(state["data"])
        return summarize(state["data"]) if not state["current"] else prompt_for(state["current"])

    if detect_booking_intent(prompt):
        state["active"] = True
        state["current"] = "name"
        return prompt_for("name")

    if rag_store["chunks"]:
        retrieved = retrieve_chunks(prompt, rag_store["chunks"], rag_store["embeddings"])
        return generate_llm_answer(prompt, "\n".join(retrieved))

    return "I do not know."
