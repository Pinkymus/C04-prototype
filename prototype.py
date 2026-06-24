from datetime import datetime
from uuid import uuid4
import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = FastAPI(
    title="ALK Metadata + RAG Readiness Prototype",
    openapi_tags=[
        {
            "name": "Prototype: Traditional Search",
            "description": "Human-readable metadata and keyword search across document records and chunks.",
        },
        {
            "name": "Prototype: RAG Retrieval",
            "description": "Simplified RAG-style retrieval using TF-IDF vectors and cosine similarity.",
        },
        {
            "name": "Prototype: Core",
            "description": "Core metadata layer, document records, tokenization, chunks, and database-style tables.",
        },
        {
            "name": "Mocks",
            "description": "Mocked company portals and services",
        }
    ],
)


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

FILE_TYPE_LABELS = {
    "FT_PDF": "PDF Document",
    "FT_DOCX": "Word Document",
    "FT_XLSX": "Excel Spreadsheet",
    "FT_PPTX": "PowerPoint Presentation",
    "FT_TXT": "Text Document",
    "FT_CSV": "CSV Dataset",
    "FT_JSON": "JSON File",
    "FT_UNKNOWN": "Unknown File Type",
}

SECURITY_LEVEL_LABELS = {
    "SEC01": "Public",
    "SEC02": "Internal",
    "SEC03": "Restricted",
    "SEC04": "Highly Restricted",
}

DEPARTMENT_LABELS = {
    "DEP_CLIN": "Clinical Development",
    "DEP_REG": "Regulatory Affairs",
    "DEP_SAFETY": "Safety",
    "DEP_RND": "Research and Development",
}

SOURCE_SYSTEM_LABELS = {
    "SRC_SP01": "SharePoint",
    "SRC_OD01": "OneDrive",
    "SRC_TEAMS01": "Microsoft Teams",
    "SRC_MANUAL": "Manual Upload",
}

VALIDATION_STATUS_LABELS = {
    "VAL_OK": "Validated",
    "VAL_PENDING": "Pending Validation",
    "VAL_FAILED": "Validation Failed",
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

def seed_demo_data():
    """
    Creates a small set of demo documents in memory.

    This makes the prototype easier to demo after every restart.
    The seed data uses the same intake pipeline as uploaded files.
    """
    if DOCUMENTS:
        return

    demo_documents = [
        DocumentIntake(
            title="Pediatric AIT Study Overview",
            file_uri="/seed-data/pediatric-ait-study-overview.txt",
            file_type_id="FT_TXT",
            security_level_id="SEC02",
            department_id="DEP_CLIN",
            source_system_id="SRC_SP01",
            validation_status_id="VAL_OK",
            owner="Sarah Green",
            text_content=(
                "This study overview describes pediatric allergen immunotherapy research. "
                "The study focuses on children and adolescents, treatment adherence, symptom reduction, "
                "long-term outcomes, and safety monitoring during allergy treatment. "
                "The work includes observations from previous clinical development projects and may be reused "
                "when designing future pediatric AIT studies."
            ),
            extra_metadata={
                "project": "Pediatric AIT",
                "seeded": True,
                "document_category": "Study overview",
            },
        ),
        DocumentIntake(
            title="ALK-depot Clinical Study Safety Report",
            file_uri="/seed-data/alk-depot-clinical-study-safety-report.txt",
            file_type_id="FT_TXT",
            security_level_id="SEC02",
            department_id="DEP_CLIN",
            source_system_id="SRC_SP01",
            validation_status_id="VAL_OK",
            owner="Sarah Green",
            text_content=(
                "This clinical study report describes ALK-depot Phase III safety results. "
                "The study followed patients receiving subcutaneous immunotherapy and monitored adverse events, "
                "dose escalation, injection site reactions, and patient compliance. "
                "The results showed acceptable safety and no unexpected safety signals."
            ),
            extra_metadata={
                "project": "ALK-depot",
                "seeded": True,
                "document_category": "Clinical Study Report",
            },
        ),
        DocumentIntake(
            title="EMA Regulatory Submission Summary",
            file_uri="/seed-data/ema-regulatory-submission-summary.txt",
            file_type_id="FT_TXT",
            security_level_id="SEC03",
            department_id="DEP_REG",
            source_system_id="SRC_SP01",
            validation_status_id="VAL_OK",
            owner="Nina Andersen",
            text_content=(
                "This regulatory submission summary describes the EMA documentation package for ALK-depot. "
                "It includes clinical efficacy, safety analysis, product quality documentation, risk management, "
                "and responses to regulatory questions from the authority."
            ),
            extra_metadata={
                "project": "ALK-depot",
                "seeded": True,
                "document_category": "Regulatory submission",
            },
        ),
        DocumentIntake(
            title="ALK-depot Dose Escalation Protocol",
            file_uri="/seed-data/alk-depot-dose-escalation-protocol.txt",
            file_type_id="FT_TXT",
            security_level_id="SEC02",
            department_id="DEP_RND",
            source_system_id="SRC_TEAMS01",
            validation_status_id="VAL_PENDING",
            owner="Martin Nielsen",
            text_content=(
                "This protocol describes the dose escalation schedule for ALK-depot subcutaneous immunotherapy. "
                "Patients begin at a low dose and gradually increase over several weeks. "
                "The protocol includes monitoring requirements, stopping rules, and criteria for continuing treatment."
            ),
            extra_metadata={
                "project": "ALK-depot",
                "seeded": True,
                "document_category": "Protocol",
            },
        ),
    ]

    for document in demo_documents:
        create_document_record(document)

@app.on_event("startup")
def startup_event():
    seed_demo_data()


def enrich_document_for_display(document: dict) -> dict:
    return {
        **document,
        "file_type_label": FILE_TYPE_LABELS.get(
            document.get("file_type_id"),
            document.get("file_type_id", "Unknown"),
        ),
        "security_level_label": SECURITY_LEVEL_LABELS.get(
            document.get("security_level_id"),
            document.get("security_level_id", "Unknown"),
        ),
        "department_label": DEPARTMENT_LABELS.get(
            document.get("department_id"),
            document.get("department_id", "Unknown"),
        ),
        "source_system_label": SOURCE_SYSTEM_LABELS.get(
            document.get("source_system_id"),
            document.get("source_system_id", "Unknown"),
        ),
        "validation_status_label": VALIDATION_STATUS_LABELS.get(
            document.get("validation_status_id"),
            document.get("validation_status_id", "Unknown"),
        ),
    }
# ---------------------------------------------------------------------
# Core API routes
# ---------------------------------------------------------------------

@app.get("/", tags=["Prototype: Core"])
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


@app.post("/documents/intake", tags=["Prototype: Core"])
def intake_document(document: DocumentIntake):
    return create_document_record(document)


@app.get("/documents", tags=["Prototype: Core"])
def get_documents():
    return list(DOCUMENTS.values())


@app.get("/documents/{document_id}", tags=["Prototype: Core"])
def get_document(document_id: str):
    if document_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail="Document not found.")

    return DOCUMENTS[document_id]


@app.get("/documents/{document_id}/tokenization", tags=["Prototype: Core"])
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


@app.get("/tables", tags=["Prototype: Core"])
def get_all_tables():
    return {
        "DOCUMENTS": list(DOCUMENTS.values()),
        "TOKENIZED_DOCUMENTS": list(TOKENIZED_DOCUMENTS.values()),
        "DOCUMENT_CHUNKS": list(DOCUMENT_CHUNKS.values()),
        "CHUNK_EMBEDDINGS": list(CHUNK_EMBEDDINGS.values()),
    }



def search_documents(
    q: str = "",
    author: str = "",
    department_id: str = "",
    security_level_id: str = "",
    source_system_id: str = "",
):
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
            " ".join(chunk["chunk_text"] for chunk in chunks),
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
                "validation_status_id": document["validation_status_id"],
                "owner": document["owner"],
                "current_tokenization_id": document["current_tokenization_id"],
                "matching_chunks": matching_chunks[:3],
                "fake_relevance_score": f"{random.randint(82, 97)}%",
            })

    return results

@app.get("/search", tags=["Prototype: Traditional Search"])
def search(
    q: str = "",
    author: str = "",
    department_id: str = "",
    security_level_id: str = "",
    source_system_id: str = "",
):
    results = search_documents(
        q=q,
        author=author,
        department_id=department_id,
        security_level_id=security_level_id,
        source_system_id=source_system_id,
    )

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

def rag_query_documents(query: RAGQuery):
    """
    Simplified RAG-style retrieval.

    This simulates the retrieval part of RAG:
    - checks access rights
    - collects accessible document chunks
    - vectorizes chunks and prompt using TF-IDF
    - compares prompt vector against chunk vectors using cosine similarity
    - returns source documents and matching chunks

    In a real implementation, TF-IDF would be replaced by embeddings
    and a vector database.
    """
    accessible_chunks = []

    for document in DOCUMENTS.values():
        if not user_can_access(document, query.user_security_clearance):
            continue

        tokenization_id = document["current_tokenization_id"]

        chunks = [
            chunk for chunk in DOCUMENT_CHUNKS.values()
            if chunk["tokenization_id"] == tokenization_id
        ]

        for chunk in chunks:
            accessible_chunks.append({
                "document": document,
                "chunk": chunk,
                "text": chunk["chunk_text"],
            })

    if not accessible_chunks:
        return {
            "prompt": query.prompt,
            "user_name": query.user_name,
            "user_security_clearance": query.user_security_clearance,
            "answer": "No accessible documents have been ingested yet.",
            "results": [],
            "retrieval_steps": [
                "Received prompt",
                "Checked user access level",
                "No accessible chunks found",
            ],
        }

    corpus = [item["text"] for item in accessible_chunks]
    corpus.append(query.prompt)

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(corpus)

    chunk_vectors = vectors[:-1]
    query_vector = vectors[-1]

    similarities = cosine_similarity(query_vector, chunk_vectors).flatten()

    ranked = sorted(
        zip(accessible_chunks, similarities),
        key=lambda pair: pair[1],
        reverse=True,
    )

    document_results = {}

    for item, similarity in ranked:
        if similarity <= 0:
            continue

        document = item["document"]
        chunk = item["chunk"]
        document_id = document["document_id"]

        if document_id not in document_results:
            document_results[document_id] = {
                "document_id": document["document_id"],
                "title": document["title"],
                "file_uri": document["file_uri"],
                "file_type_id": document["file_type_id"],
                "security_level_id": document["security_level_id"],
                "department_id": document["department_id"],
                "source_system_id": document["source_system_id"],
                "validation_status_id": document["validation_status_id"],
                "owner": document["owner"],
                "current_tokenization_id": document["current_tokenization_id"],
                "matching_chunks": [],
                "score": 0,
                "fake_relevance_score": 0,
            }

        document_results[document_id]["matching_chunks"].append({
            **chunk,
            "similarity": round(float(similarity), 4),
        })

        document_results[document_id]["score"] += float(similarity)

    results = list(document_results.values())

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    results = results[:query.max_results]

    # for result in results:
    #     result["matching_chunks"] = result["matching_chunks"][:2]
    #     result["fake_relevance_score"] = min(
    #         98,
    #         max(60, round(result["score"] * 100)),
    #     )

    for rank, result in enumerate(results):
        result["matching_chunks"] = result["matching_chunks"][:2]

        raw_score = float(result["score"])

        # Demo-friendly score.
        # TF-IDF cosine scores are often small, so this maps them into a clearer
        # presentation range without claiming to be a real model confidence score.
        scaled_score = 62 + round(raw_score * 180)

        # Small rank adjustment so the best result looks clearly best.
        scaled_score -= rank * 6

        result["fake_relevance_score"] = min(
            98,
            max(60, scaled_score),
        )

    if not results:
        return {
            "prompt": query.prompt,
            "user_name": query.user_name,
            "user_security_clearance": query.user_security_clearance,
            "answer": (
                "No accessible documents matched the query. "
                "The relevant documents may not have been ingested yet, "
                "or the user may not have access."
            ),
            "results": [],
            "retrieval_steps": [
                "Received prompt",
                "Checked user access level",
                "Vectorized prompt using TF-IDF",
                "Compared prompt against document chunks",
                "No matching accessible chunks found",
            ],
        }

    cited_titles = ", ".join(result["title"] for result in results)

    return {
        "prompt": query.prompt,
        "user_name": query.user_name,
        "user_security_clearance": query.user_security_clearance,
        "answer": (
            f"Based on the accessible RAG Compass records, the most relevant source documents are: "
            f"{cited_titles}. The prototype retrieved these by comparing the prompt against tokenized "
            f"document chunks and returning the closest matches with source references."
        ),
        "results": results,
        "retrieval_steps": [
            "Received prompt",
            "Checked user access level",
            "Vectorized prompt using TF-IDF",
            "Compared prompt against tokenized document chunks",
            "Returned accessible documents with source references",
        ],
    }

@app.post("/rag-compass/query", tags=["Prototype: RAG Retrieval"])
def rag_compass_query(query: RAGQuery):
    return rag_query_documents(query)

# ---------------------------------------------------------------------
# Register mock external systems
# ---------------------------------------------------------------------
# These imports add their own routes to the same FastAPI app.
# Keep them at the bottom so app, models, and shared functions exist first.

import fake_sharepoint  # noqa: E402,F401
import fake_internal_ai  # noqa: E402,F401
import fake_regulatory_checklist  # noqa: E402,F401
import fake_reuse_checker  # noqa: E402,F401