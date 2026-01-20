import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> np.ndarray:
    return model.encode(text)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def embed_bookings(bookings):
    embedded = []

    for booking in bookings:
        text = (
            f"{booking['name']} "
            f"{booking['email']} "
            f"{booking['date']} "
            f"{booking['hotel']}"
        )

        vector = get_embedding(text)

        embedded.append({
            "booking": booking,
            "vector": vector
        })

    return embedded


def search_bookings(query_embedding, embedded_bookings, top_k=3):
    scores = []

    for item in embedded_bookings:
        score = cosine_similarity(query_embedding, item["vector"])
        scores.append((score, item["booking"]))

    scores.sort(key=lambda x: x[0], reverse=True)
    return [b for _, b in scores[:top_k]]
