from datetime import datetime
from uuid import uuid4
import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(title="ALK Metadata + RAG Readiness Prototype")


# ---------------------------------------------------------------------
# In-memory "database tables"
# ---------------------------------------------------------------------

DOCUMENTS = {}
TOKENIZED_DOCUMENTS = {}
DOCUMENT_CHUNKS = {}
CHUNK_EMBEDDINGS = {}


# ---------------------------------------------------------------------
# Lookup / definition values
# ---------------------------------------------------------------------

FILE_TYPE_BY_EXTENSION = {
    ".pdf": "FT_PDF",
    ".docx": "FT_DOCX",
    ".xlsx": "FT_XLSX",
    ".pptx": "FT_PPTX",
    ".txt": "FT_TXT",
    ".csv": "FT_CSV",
    ".md": "FT_TXT",
    ".json": "FT_JSON",
}


SECURITY_RANK = {
    "SEC01": 1,  # Public / low sensitivity
    "SEC02": 2,  # Internal
    "SEC03": 3,  # Restricted
    "SEC04": 4,  # Highly restricted
}


# ---------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------

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
    extra_metadata: dict = Field(default_factory=dict)


class RAGQuery(BaseModel):
    prompt: str
    user_name: str = "Sarah Green"
    user_security_clearance: str = "SEC03"
    max_results: int = 2


# ---------------------------------------------------------------------
# Shared helper functions
# ---------------------------------------------------------------------

def chunk_tokens(tokens: list[str], chunk_size: int = 80, overlap: int = 10):
    """
    Prototype chunking.

    In the real system, this would likely use model-specific tokenization
    and chunking based on the chosen embedding model.
    """
    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(tokens[start:end])

        if end == len(tokens):
            break

        start += chunk_size - overlap

    return chunks


def user_can_access(document: dict, user_security_clearance: str) -> bool:
    """
    Simple access-control simulation.

    A user can access a document if their clearance rank is equal to or
    higher than the document's security level.
    """
    document_level = document.get("security_level_id", "SEC04")
    user_rank = SECURITY_RANK.get(user_security_clearance, 0)
    document_rank = SECURITY_RANK.get(document_level, 999)

    return user_rank >= document_rank


def create_document_record(document: DocumentIntake):
    """
    Core intake function.

    This simulates the metadata + RAG-readiness layer:
    - creates a DOCUMENT record
    - creates a TOKENIZED_DOCUMENT record
    - splits document text into chunks
    - creates fake embedding records
    - stores everything in in-memory dictionaries
    """
    if not document.text_content.strip():
        raise HTTPException(
            status_code=400,
            detail="Document text is required for RAG processing.",
        )

    document_id = f"DOC-{uuid4().hex[:8].upper()}"
    tokenization_id = f"TOK-{uuid4().hex[:8].upper()}"

    # Prototype tokenization: simple word splitting.
    # For the demo, TXT files are actually read, split, chunked, and searched.
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
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    TOKENIZED_DOCUMENTS[tokenization_id] = {
        "tokenization_id": tokenization_id,
        "document_id": document_id,
        "tokenizer_name": "prototype-word-split-tokenizer",
        "total_tokens": len(tokens),
        "tokenized_at": datetime.now().isoformat(timespec="seconds"),
        "tokenization_settings": {
            "chunk_size": 80,
            "overlap": 10,
            "note": (
                "Prototype tokenizer. Real system would use model-specific "
                "tokenization and embedding-compatible chunking."
            ),
        },
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
            "chunk_text": " ".join(chunk),
        }

        # Fake embedding record.
        # The actual RAG emulation happens in fake_internal_ai.py using TF-IDF.
        # This is kept to mirror the database design.
        CHUNK_EMBEDDINGS[embedding_id] = {
            "embedding_id": embedding_id,
            "chunk_id": chunk_id,
            "embedding_model": "fake-prototype-embedding",
            "vector_dimensions": 8,
            "embedding_vector": [round(random.random(), 4) for _ in range(8)],
        }

        created_chunks.append(chunk_id)

    return {
        "message": "Document ingested and made RAG-ready.",
        "document_id": document_id,
        "tokenization_id": tokenization_id,
        "chunks_created": len(created_chunks),
        "status": "Ready",
        "document_record": DOCUMENTS[document_id],
        "tokenization_record": TOKENIZED_DOCUMENTS[tokenization_id],
    }


# ---------------------------------------------------------------------
# Core API routes
# ---------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "ALK RAG Compass prototype is running.",
        "pages": {
            "mock_sharepoint": "/sharepoint",
            "mock_internal_ai": "/ai",
            "api_docs": "/docs",
            "all_tables": "/tables",
        },
    }


@app.post("/documents/intake")
def intake_document(document: DocumentIntake):
    return create_document_record(document)


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

    chunk_ids = {chunk["chunk_id"] for chunk in chunks}

    embeddings = [
        embedding for embedding in CHUNK_EMBEDDINGS.values()
        if embedding["chunk_id"] in chunk_ids
    ]

    return {
        "document": document,
        "tokenization": TOKENIZED_DOCUMENTS[tokenization_id],
        "chunks": chunks,
        "embeddings": embeddings,
    }


@app.get("/tables")
def get_all_tables():
    return {
        "DOCUMENTS": list(DOCUMENTS.values()),
        "TOKENIZED_DOCUMENTS": list(TOKENIZED_DOCUMENTS.values()),
        "DOCUMENT_CHUNKS": list(DOCUMENT_CHUNKS.values()),
        "CHUNK_EMBEDDINGS": list(CHUNK_EMBEDDINGS.values()),
    }


@app.get("/search")
def search(
    q: str = "",
    author: str = "",
    department_id: str = "",
    security_level_id: str = "",
    source_system_id: str = "",
):
    """
    Simple metadata + keyword search.

    This is separate from the RAG-like retrieval in fake_internal_ai.py.
    It is useful for showing classic metadata filtering.
    """
    query = q.lower().strip()
    author_query = author.lower().strip()
    department_query = department_id.lower().strip()
    security_query = security_level_id.lower().strip()
    source_query = source_system_id.lower().strip()

    results = []

    for document in DOCUMENTS.values():
        tokenization_id = document["current_tokenization_id"]

        chunks = [
            chunk for chunk in DOCUMENT_CHUNKS.values()
            if chunk["tokenization_id"] == tokenization_id
        ]

        searchable_document_text = " ".join([
            str(document.get("document_id", "")),
            str(document.get("title", "")),
            str(document.get("file_uri", "")),
            str(document.get("file_type_id", "")),
            str(document.get("security_level_id", "")),
            str(document.get("department_id", "")),
            str(document.get("source_system_id", "")),
            str(document.get("validation_status_id", "")),
            str(document.get("owner", "")),
            str(document.get("extra_metadata", "")),
        ]).lower()

        matching_chunks = [
            chunk for chunk in chunks
            if query and query in chunk["chunk_text"].lower()
        ]

        matches_text_search = (
            not query
            or query in searchable_document_text
            or len(matching_chunks) > 0
        )

        matches_author = (
            not author_query
            or author_query in str(document.get("owner", "")).lower()
        )

        matches_department = (
            not department_query
            or department_query == str(document.get("department_id", "")).lower()
        )

        matches_security = (
            not security_query
            or security_query == str(document.get("security_level_id", "")).lower()
        )

        matches_source = (
            not source_query
            or source_query == str(document.get("source_system_id", "")).lower()
        )

        if (
            matches_text_search
            and matches_author
            and matches_department
            and matches_security
            and matches_source
        ):
            results.append({
                "document_id": document["document_id"],
                "title": document["title"],
                "file_uri": document["file_uri"],
                "file_type_id": document["file_type_id"],
                "security_level_id": document["security_level_id"],
                "department_id": document["department_id"],
                "source_system_id": document["source_system_id"],
                "owner": document["owner"],
                "current_tokenization_id": document["current_tokenization_id"],
                "matching_chunks": matching_chunks[:3],
                "fake_relevance_score": f"{random.randint(82, 97)}%",
            })

    return {
        "query": q,
        "filters": {
            "author": author,
            "department_id": department_id,
            "security_level_id": security_level_id,
            "source_system_id": source_system_id,
        },
        "results_found": len(results),
        "results": results,
    }


# ---------------------------------------------------------------------
# Register mock external systems
# ---------------------------------------------------------------------
# These imports add their own routes to the same FastAPI app.
# Keep them at the bottom so app, models, and shared functions exist first.

import fake_sharepoint  # noqa: E402,F401
import fake_internal_ai  # noqa: E402,F401