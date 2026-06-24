from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
import random

app = FastAPI(title="ALK Metadata + RAG Readiness Prototype")

DOCUMENTS = {}
TOKENIZED_DOCUMENTS = {}
DOCUMENT_CHUNKS = {}
CHUNK_EMBEDDINGS = {}

class DocumentIntake(BaseModel):
    title: str
    file_uri: str
    file_type_id: str
    security_level_id: str
    department_id: str
    source_system_id: str
    validation_status_id: str
    owner: str
    text_content: str
    extra_metadata: dict = {}

def chunk_tokens(tokens, chunk_size=80, overlap=10):
    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(tokens[start:end])
        start += chunk_size - overlap

    return chunks

@app.post("/documents/intake")
def intake_document(document: DocumentIntake):
    if not document.text_content.strip():
        raise HTTPException(status_code=400, detail="Document text is required for RAG processing.")

    document_id = f"DOC-{uuid4().hex[:8].upper()}"
    tokenization_id = f"TOK-{uuid4().hex[:8].upper()}"

    tokens = document.text_content.split()
    chunks = chunk_tokens(tokens)

    DOCUMENTS[document_id] = {
        "document_id": document_id,
        "title": document.title,
        "file_uri": document.file_uri,
        "file_type_id": document.file_type_id,
        "security_level_id": document.security_level_id,
        "department_id": document.department_id,
        "source_system_id": document.source_system_id,
        "validation_status_id": document.validation_status_id,
        "owner": document.owner,
        "current_tokenization_id": tokenization_id,
        "extra_metadata": document.extra_metadata,
        "created_at": datetime.now().isoformat()
    }

    TOKENIZED_DOCUMENTS[tokenization_id] = {
        "tokenization_id": tokenization_id,
        "document_id": document_id,
        "tokenizer_name": "prototype-word-split-tokenizer",
        "total_tokens": len(tokens),
        "tokenized_at": datetime.now().isoformat(),
        "tokenization_settings": {
            "chunk_size": 80,
            "overlap": 10
        }
    }

    created_chunks = []

    for index, chunk in enumerate(chunks):
        chunk_id = f"CHK-{uuid4().hex[:8].upper()}"
        embedding_id = f"EMB-{uuid4().hex[:8].upper()}"

        DOCUMENT_CHUNKS[chunk_id] = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "tokenization_id": tokenization_id,
            "chunk_index": index,
            "chunk_text": " ".join(chunk)
        }

        CHUNK_EMBEDDINGS[embedding_id] = {
            "embedding_id": embedding_id,
            "chunk_id": chunk_id,
            "embedding_model": "fake-prototype-embedding",
            "vector_dimensions": 8,
            "embedding_vector": [round(random.random(), 4) for _ in range(8)]
        }

        created_chunks.append(chunk_id)

    return {
        "message": "Document ingested and made RAG-ready.",
        "document_id": document_id,
        "tokenization_id": tokenization_id,
        "chunks_created": len(created_chunks),
        "status": "Ready"
    }

@app.get("/documents")
def get_documents():
    return list(DOCUMENTS.values())

@app.get("/documents/{document_id}")
def get_document(document_id: str):
    if document_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DOCUMENTS[document_id]

@app.get("/documents/{document_id}/tokenization")
def get_tokenization(document_id: str):
    document = DOCUMENTS.get(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    tokenization_id = document["current_tokenization_id"]

    chunks = [
        chunk for chunk in DOCUMENT_CHUNKS.values()
        if chunk["tokenization_id"] == tokenization_id
    ]

    embeddings = [
        embedding for embedding in CHUNK_EMBEDDINGS.values()
        if embedding["chunk_id"] in [chunk["chunk_id"] for chunk in chunks]
    ]

    return {
        "document": document,
        "tokenization": TOKENIZED_DOCUMENTS[tokenization_id],
        "chunks": chunks,
        "embeddings": embeddings
    }

@app.get("/search")
def search(q: str):
    query = q.lower()
    results = []

    for document in DOCUMENTS.values():
        matching_chunks = [
            chunk for chunk in DOCUMENT_CHUNKS.values()
            if chunk["document_id"] == document["document_id"]
            and query in chunk["chunk_text"].lower()
        ]

        if query in document["title"].lower() or matching_chunks:
            results.append({
                "document_id": document["document_id"],
                "title": document["title"],
                "file_uri": document["file_uri"],
                "security_level_id": document["security_level_id"],
                "matching_chunks": matching_chunks[:3],
                "fake_relevance_score": f"{random.randint(82, 97)}%"
            })

    return results