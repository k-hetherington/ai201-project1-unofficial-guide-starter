import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, create_chunks

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "professor_reviews"


def build_vector_store():
    documents = load_documents()
    chunks = create_chunks(documents)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)

    texts = [chunk["text"] for chunk in chunks]
    ids = [f'{chunk["source"]}_{chunk["chunk_id"]}' for chunk in chunks]
    metadatas = [
        {
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"]
        }
        for chunk in chunks
    ]

    embeddings = model.encode(texts).tolist()

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB")


def search(query, top_k=4):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    query_embedding = model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    for i in range(len(results["documents"][0])):
        print("=" * 50)
        print("Source:", results["metadatas"][0][i]["source"])
        print("Distance:", results["distances"][0][i])
        print(results["documents"][0][i])


if __name__ == "__main__":
    build_vector_store()

    print("\nTest query results:\n")
    search("Which professor has the heaviest workload?")