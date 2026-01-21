import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from llm import llm_answer

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, size=400):
    return [text[i:i+size] for i in range(0, len(text), size)]

def embed_chunks(chunks):
    return embedder.encode(chunks)

def retrieve(query, chunks, embeddings, k=3):
    q_emb = embedder.encode([query])
    sims = cosine_similarity(q_emb, embeddings)[0]
    idx = sims.argsort()[-k:][::-1]
    return [chunks[i] for i in idx]

def rag_answer(question, chunks, embeddings):
    retrieved = retrieve(question, chunks, embeddings)
    if not retrieved:
        return "I do not know."
    context = "\n".join(retrieved)
    return llm_answer(question, context)

def extract_fields_from_text(text):
    data = {}
    email = re.search(r"[\w.-]+@[\w.-]+\.\w+", text)
    phone = re.search(r"\b\d{10}\b", text)
    name = re.search(r"Name[:\- ]+([A-Za-z ]+)", text)
    date = re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)
    time = re.search(r"\b\d{1,2}:\d{2}\s?(AM|PM|am|pm)?\b", text)

    if email: data["email"] = email.group()
    if phone: data["phone"] = phone.group()
    if name: data["name"] = name.group(1).strip()
    if date: data["date"] = date.group()
    if time: data["time"] = time.group()

    return data
