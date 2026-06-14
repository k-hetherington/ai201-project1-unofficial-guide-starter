from pathlib import Path

DOCUMENTS_DIR = Path("documents")

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def load_documents():
    documents = []

    for file_path in DOCUMENTS_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": file_path.name,
            "text": text
        })

    return documents


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_chunks(documents):
    all_chunks = []

    for document in documents:
        chunks = chunk_text(document["text"])

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "source": document["source"],
                "chunk_id": index,
                "text": chunk
            })

    return all_chunks


if __name__ == "__main__":
    documents = load_documents()

    print(f"Loaded {len(documents)} documents")

    chunks = create_chunks(documents)

    print(f"Created {len(chunks)} chunks")

    print("\nSample Chunks:\n")

    for chunk in chunks[:5]:
        print("=" * 50)
        print(chunk["source"])
        print(chunk["text"])
        print()