from groq import Groq
from dotenv import load_dotenv
import os

import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(name=COLLECTION_NAME)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def retrieve(query, top_k=4):
    query_embedding = embedding_model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


def ask(question):
    results = retrieve(question)

    retrieved_chunks = results["documents"][0]
    retrieved_metadata = results["metadatas"][0]

    context_parts = []
    sources = []

    for i, chunk in enumerate(retrieved_chunks):
        source = retrieved_metadata[i]["source"]

        context_parts.append(
            f"Source: {source}\nText:\n{chunk}"
        )

        sources.append(source)

    context = "\n\n".join(context_parts)

    prompt = f"""
You are answering questions about professor reviews.

Use ONLY the information contained in the provided context.

If the answer exists in the context, answer directly and cite the source file.

If the answer is not present in the context, respond exactly:
"I don't have enough information to answer that."

Context:
{context}

Question:
{question}
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": list(set(sources))
    }


if __name__ == "__main__":
    question = "Which professor has the heaviest workload?"

    result = ask(question)

    print("\nQUESTION:")
    print(question)

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print("-", source)