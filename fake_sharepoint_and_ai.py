class RAGQuery(BaseModel):
    prompt: str
    user_name: str = "Sarah Green"
    user_security_clearance: str = "SEC03"
    max_results: int = 2


SECURITY_RANK = {
    "SEC01": 1,
    "SEC02": 2,
    "SEC03": 3,
    "SEC04": 4,
}


STOPWORDS = {
    "the", "and", "or", "a", "an", "to", "of", "in", "on", "for", "with",
    "is", "are", "was", "were", "what", "which", "show", "find", "me",
    "about", "from", "that", "this", "can", "i", "we", "it"
}


def user_can_access(document: dict, user_security_clearance: str) -> bool:
    document_level = document.get("security_level_id", "SEC04")
    user_rank = SECURITY_RANK.get(user_security_clearance, 0)
    document_rank = SECURITY_RANK.get(document_level, 999)

    return user_rank >= document_rank


def keywords_from_prompt(prompt: str):
    cleaned = (
        prompt.lower()
        .replace("?", " ")
        .replace(".", " ")
        .replace(",", " ")
        .replace(":", " ")
        .replace(";", " ")
        .replace("-", " ")
        .replace("_", " ")
    )

    return [
        word for word in cleaned.split()
        if len(word) > 2 and word not in STOPWORDS
    ]


@app.post("/rag-compass/query")
def rag_compass_query(query: RAGQuery):
    keywords = keywords_from_prompt(query.prompt)
    results = []

    for document in DOCUMENTS.values():
        if not user_can_access(document, query.user_security_clearance):
            continue

        tokenization_id = document["current_tokenization_id"]

        chunks = [
            chunk for chunk in DOCUMENT_CHUNKS.values()
            if chunk["tokenization_id"] == tokenization_id
        ]

        searchable_text = " ".join([
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

        score = sum(1 for keyword in keywords if keyword in searchable_text)

        if score > 0:
            matching_chunks = [
                chunk for chunk in chunks
                if any(keyword in chunk["chunk_text"].lower() for keyword in keywords)
            ]

            results.append({
                "document_id": document["document_id"],
                "title": document["title"],
                "file_uri": document["file_uri"],
                "security_level_id": document["security_level_id"],
                "department_id": document["department_id"],
                "source_system_id": document["source_system_id"],
                "current_tokenization_id": document["current_tokenization_id"],
                "matching_chunks": matching_chunks[:2],
                "score": score,
                "fake_relevance_score": min(98, 78 + score * 6),
            })

    results.sort(key=lambda item: item["score"], reverse=True)
    results = results[:query.max_results]

    if not results:
        return {
            "prompt": query.prompt,
            "user_name": query.user_name,
            "user_security_clearance": query.user_security_clearance,
            "answer": "No accessible documents matched the query. The user may lack access, or the relevant documents may not have been ingested yet.",
            "results": [],
            "retrieval_steps": [
                "Received prompt from internal AI assistant",
                "Checked user access level",
                "Searched metadata and document chunks",
                "No accessible matches found"
            ]
        }

    cited_titles = ", ".join(result["title"] for result in results)

    return {
        "prompt": query.prompt,
        "user_name": query.user_name,
        "user_security_clearance": query.user_security_clearance,
        "answer": (
            f"Based on the accessible RAG Compass records, the most relevant documents are: "
            f"{cited_titles}. These documents were retrieved from the metadata layer and linked back "
            f"to their original source locations."
        ),
        "results": results,
        "retrieval_steps": [
            "Received prompt from internal AI assistant",
            "Checked user access level",
            "Searched document metadata",
            "Searched tokenized document chunks",
            "Returned accessible documents with citations"
        ]
    }