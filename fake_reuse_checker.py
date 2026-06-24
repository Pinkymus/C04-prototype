from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from prototype import (
    app,
    RAGQuery,
    search_documents,
    rag_query_documents,
)


class ReuseCheckRequest(BaseModel):
    project_idea: str
    user_name: str = "Sarah Green"
    user_security_clearance: str = "SEC03"


def extract_metadata_terms(project_idea: str) -> list[str]:
    ignored_terms = {
        "with", "focus", "study", "studies", "research", "project",
        "new", "idea", "and", "the", "for", "from", "that", "this",
    }

    normalized = (
        project_idea
        .replace("-", " ")
        .replace("_", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace(":", " ")
        .replace(";", " ")
        .lower()
    )

    terms = []

    for term in normalized.split():
        if len(term) <= 3:
            continue

        if term in ignored_terms:
            continue

        if term not in terms:
            terms.append(term)

    return terms[:10]


def traditional_reuse_search(project_idea: str):
    terms = extract_metadata_terms(project_idea)
    scored_documents = {}

    for term in terms:
        search_results = search_documents(q=term)

        for result in search_results:
            document_id = result["document_id"]

            if document_id not in scored_documents:
                scored_documents[document_id] = {
                    "document": result,
                    "score": 0,
                    "matched_terms": [],
                }

            scored_documents[document_id]["score"] += 1
            scored_documents[document_id]["matched_terms"].append(term)

    ranked = sorted(
        scored_documents.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    results = []

    for item in ranked:
        document = item["document"]

        results.append({
            **document,
            "metadata_match_score": item["score"],
            "matched_metadata_terms": item["matched_terms"],
        })

    return {
        "query_terms": terms,
        "results": results,
    }


@app.post("/reuse/check", tags=["Mocks"])
def reuse_check(request: ReuseCheckRequest):
    metadata_search = traditional_reuse_search(request.project_idea)
    metadata_results = metadata_search["results"]

    rag_result = rag_query_documents(
        RAGQuery(
            prompt=(
                "Find previous work that could be reused or could make this new research idea duplicate work: "
                + request.project_idea
            ),
            user_name=request.user_name,
            user_security_clearance=request.user_security_clearance,
            max_results=3,
        )
    )

    metadata_document_ids = {
        result["document_id"]
        for result in metadata_results
    }

    rag_document_ids = {
        result["document_id"]
        for result in rag_result["results"]
    }

    overlap_document_ids = metadata_document_ids.intersection(rag_document_ids)

    if overlap_document_ids:
        reuse_risk = "High reuse potential"
        recommendation = (
            "The traditional metadata search and RAG-style retrieval found the same related document(s). "
            "This strongly suggests that relevant work already exists and should be reviewed before starting new work."
        )
    elif rag_result["results"] and metadata_results:
        reuse_risk = "Medium reuse potential"
        recommendation = (
            "Both search methods found related documents, but they did not identify the exact same records. "
            "The project may still benefit from reviewing previous work."
        )
    elif rag_result["results"] or metadata_results:
        reuse_risk = "Low reuse potential"
        recommendation = (
            "Some related material was found, but the match is weak. "
            "The idea may be new, or relevant documents may not have been fully ingested yet."
        )
    else:
        reuse_risk = "No obvious reuse found"
        recommendation = (
            "No related accessible documents were found. "
            "This does not prove that no previous work exists, only that the current metadata layer did not find it."
        )

    return {
        "project_idea": request.project_idea,
        "user_name": request.user_name,
        "user_security_clearance": request.user_security_clearance,
        "reuse_risk": reuse_risk,
        "recommendation": recommendation,
        "traditional_search": {
            "query": " + ".join(metadata_search["query_terms"]),
            "query_terms": metadata_search["query_terms"],
            "results_found": len(metadata_results),
            "results": metadata_results[:5],
        },
        "rag_retrieval": rag_result,
        "overlap_document_ids": list(overlap_document_ids),
    }

@app.get("/reuse-checker", response_class=HTMLResponse, tags=["Mocks"])
def reuse_checker_page():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
<head>
    <title>Research Reuse Checker</title>
    <style>
        :root {
            --bg: #0f172a;
            --panel: #111827;
            --panel-2: #1f2937;
            --card: #f8fafc;
            --text: #e5e7eb;
            --muted: #94a3b8;
            --lime: #a3e635;
            --cyan: #22d3ee;
            --purple: #c084fc;
            --orange: #fb923c;
            --red: #f87171;
            --green: #4ade80;
            --border: #334155;
            --dark-text: #172033;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background:
                radial-gradient(circle at top right, rgba(34, 211, 238, 0.18), transparent 35%),
                radial-gradient(circle at bottom left, rgba(192, 132, 252, 0.16), transparent 35%),
                var(--bg);
            color: var(--text);
        }

        .header {
            padding: 34px 48px 24px 48px;
            border-bottom: 1px solid var(--border);
        }

        .eyebrow {
            color: var(--lime);
            font-weight: bold;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            font-size: 12px;
        }

        h1 {
            margin: 10px 0 8px 0;
            font-size: 38px;
        }

        .subtitle {
            color: var(--muted);
            max-width: 820px;
            line-height: 1.5;
            margin: 0;
        }

        .container {
            max-width: 1180px;
            margin: 30px auto;
            padding: 0 24px 40px 24px;
        }

        .input-card {
            background: rgba(17, 24, 39, 0.92);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 24px;
            box-shadow: 0 18px 45px rgba(0,0,0,0.28);
        }

        label {
            display: block;
            color: var(--muted);
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 13px;
        }

        textarea {
            width: 100%;
            min-height: 105px;
            box-sizing: border-box;
            background: #020617;
            border: 1px solid var(--border);
            border-radius: 16px;
            color: var(--text);
            font-size: 16px;
            font-family: Arial, sans-serif;
            padding: 16px;
            resize: vertical;
            outline: none;
        }

        .controls {
            margin-top: 16px;
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 12px;
            align-items: end;
        }

        input, select {
            width: 100%;
            box-sizing: border-box;
            background: #020617;
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text);
            padding: 11px 12px;
            font-size: 14px;
        }

        button {
            height: 42px;
            background: linear-gradient(135deg, var(--cyan), var(--purple));
            color: #020617;
            border: none;
            border-radius: 12px;
            padding: 0 20px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            filter: brightness(1.08);
        }

        .links {
            margin-top: 14px;
            display: flex;
            gap: 14px;
        }

        .links a {
            color: var(--cyan);
            text-decoration: none;
            font-size: 14px;
            font-weight: bold;
        }

        .summary {
            margin-top: 24px;
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 20px;
        }

        .result-panel {
            background: rgba(17, 24, 39, 0.92);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 24px;
            box-shadow: 0 18px 45px rgba(0,0,0,0.22);
        }

        .risk {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .risk.high {
            color: var(--green);
        }

        .risk.medium {
            color: var(--orange);
        }

        .risk.low {
            color: var(--cyan);
        }

        .risk.none {
            color: var(--muted);
        }

        .recommendation {
            color: var(--muted);
            line-height: 1.5;
        }

        .pipeline {
            display: grid;
            gap: 12px;
        }

        .pipe-step {
            background: #020617;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
        }

        .pipe-title {
            font-weight: bold;
            color: var(--text);
        }

        .pipe-body {
            color: var(--muted);
            margin-top: 5px;
            font-size: 14px;
            line-height: 1.45;
        }

        .columns {
            margin-top: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .column-card {
            background: rgba(17, 24, 39, 0.92);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 22px;
        }

        .column-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .column-title h2 {
            margin: 0;
            font-size: 22px;
        }

        .tag {
            border-radius: 999px;
            padding: 5px 9px;
            font-size: 12px;
            font-weight: bold;
        }

        .tag.metadata {
            background: rgba(34, 211, 238, 0.15);
            color: var(--cyan);
        }

        .tag.rag {
            background: rgba(192, 132, 252, 0.15);
            color: var(--purple);
        }

        .doc-card {
            background: #f8fafc;
            color: var(--dark-text);
            border-radius: 16px;
            padding: 15px;
            margin-bottom: 12px;
        }

        .doc-card h3 {
            margin: 0 0 8px 0;
            font-size: 16px;
        }

        .doc-meta {
            color: #64748b;
            font-size: 13px;
            line-height: 1.5;
        }

        .chunk {
            margin-top: 10px;
            background: #eef2ff;
            border-left: 4px solid #8b5cf6;
            padding: 10px;
            border-radius: 10px;
            font-size: 13px;
            color: #334155;
            line-height: 1.45;
        }

        .empty {
            color: var(--muted);
            padding: 10px 0;
        }

        .loading {
            margin-top: 24px;
            background: rgba(17, 24, 39, 0.92);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px;
            color: var(--muted);
        }
    </style>
</head>

<body>
    <div class="header">
        <div class="eyebrow">Research reuse and duplicate work prevention</div>
        <h1>Research Reuse Checker</h1>
        <p class="subtitle">
            This mock system combines traditional metadata search with simplified RAG-style retrieval.
            It checks whether a new research idea overlaps with existing validated knowledge.
        </p>
    </div>

    <div class="container">
        <div class="input-card">
            <label>New research idea</label>
            <textarea id="projectIdea">Pediatric allergen immunotherapy adherence study with focus on symptom reduction, long-term outcomes, and safety monitoring</textarea>

            <div class="controls">
                <div>
                    <label>User</label>
                    <input id="userName" value="Sarah Green">
                </div>

                <div>
                    <label>Clearance</label>
                    <select id="clearance">
                        <option value="SEC02">SEC02 Internal</option>
                        <option value="SEC03" selected>SEC03 Restricted</option>
                        <option value="SEC04">SEC04 Highly Restricted</option>
                    </select>
                </div>

                <button onclick="runReuseCheck()">Check reuse</button>
            </div>
        </div>

        <div id="output"></div>
    </div>

    <script>
        async function runReuseCheck() {
            const output = document.getElementById("output");

            const projectIdea = document.getElementById("projectIdea").value;
            const userName = document.getElementById("userName").value;
            const clearance = document.getElementById("clearance").value;

            output.innerHTML = `
                <div class="loading">
                    Running traditional metadata search and simplified RAG retrieval...
                </div>
            `;

            await sleep(700);

            const response = await fetch("/reuse/check", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    project_idea: projectIdea,
                    user_name: userName,
                    user_security_clearance: clearance
                })
            });

            const data = await response.json();

            renderOutput(data);
        }

        function renderOutput(data) {
            const output = document.getElementById("output");

            const riskClass = getRiskClass(data.reuse_risk);

            let html = `
                <div class="summary">
                    <div class="result-panel">
                        <div class="risk ${riskClass}">${escapeHtml(data.reuse_risk)}</div>
                        <div class="recommendation">${escapeHtml(data.recommendation)}</div>
                    </div>

                    <div class="result-panel">
                        <div class="pipeline">
                            <div class="pipe-step">
                                <div class="pipe-title">1. Traditional metadata search</div>
                                <div class="pipe-body">
                                    Query: ${escapeHtml(data.traditional_search.query)}<br>
                                    Found ${data.traditional_search.results_found} document record(s).
                                </div>
                            </div>

                            <div class="pipe-step">
                                <div class="pipe-title">2. RAG retrieval</div>
                                <div class="pipe-body">
                                    ${escapeHtml(data.rag_retrieval.retrieval_steps.join(" → "))}
                                </div>
                            </div>

                            <div class="pipe-step">
                                <div class="pipe-title">3. Combined decision</div>
                                <div class="pipe-body">
                                    Overlapping documents: ${data.overlap_document_ids.length}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="columns">
                    <div class="column-card">
                        <div class="column-title">
                            <h2>Metadata search results</h2>
                            <span class="tag metadata">Traditional search</span>
                        </div>
                        ${renderMetadataResults(data.traditional_search.results)}
                    </div>

                    <div class="column-card">
                        <div class="column-title">
                            <h2>RAG retrieval results</h2>
                            <span class="tag rag">TF-IDF similarity</span>
                        </div>
                        ${renderRagResults(data.rag_retrieval.results)}
                    </div>
                </div>
            `;

            output.innerHTML = html;
        }

        function renderMetadataResults(results) {
            if (!results || results.length === 0) {
                return `<div class="empty">No matching metadata records found.</div>`;
            }

            let html = "";

            for (const doc of results) {
                html += `
                    <div class="doc-card">
                        <h3>${escapeHtml(doc.title)}</h3>
                        <div class="doc-meta">
                            Document ID: ${escapeHtml(doc.document_id)}<br>
                            Owner: ${escapeHtml(doc.owner)}<br>
                            Department: ${escapeHtml(doc.department_id)}
                            · Security: ${escapeHtml(doc.security_level_id)}
                            · Validation: ${escapeHtml(doc.validation_status_id)}<br>
                            Source: ${escapeHtml(doc.file_uri)}<br>
                            Tokenization: ${escapeHtml(doc.current_tokenization_id)}
                        </div>
                    </div>
                `;
            }

            return html;
        }

        function renderRagResults(results) {
            if (!results || results.length === 0) {
                return `<div class="empty">No RAG-style matches found.</div>`;
            }

            let html = "";

            for (const doc of results) {
                let chunkHtml = "";

                if (doc.matching_chunks && doc.matching_chunks.length > 0) {
                    chunkHtml = `
                        <div class="chunk">
                            <strong>Closest chunk:</strong><br>
                            ${escapeHtml(truncate(doc.matching_chunks[0].chunk_text, 300))}
                        </div>
                    `;
                }

                html += `
                    <div class="doc-card">
                        <h3>${escapeHtml(doc.title)}</h3>
                        <div class="doc-meta">
                            Relevance: ${escapeHtml(doc.fake_relevance_score)}%<br>
                            Document ID: ${escapeHtml(doc.document_id)}<br>
                            Security: ${escapeHtml(doc.security_level_id)}
                            · Source: ${escapeHtml(doc.file_uri)}<br>
                            Tokenization: ${escapeHtml(doc.current_tokenization_id)}
                        </div>
                        ${chunkHtml}
                    </div>
                `;
            }

            return html;
        }

        function getRiskClass(risk) {
            const text = String(risk).toLowerCase();

            if (text.includes("high")) return "high";
            if (text.includes("medium")) return "medium";
            if (text.includes("low")) return "low";
            return "none";
        }

        function truncate(text, maxLength) {
            if (!text) return "";
            if (text.length <= maxLength) return text;
            return text.slice(0, maxLength) + "...";
        }

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        function escapeHtml(value) {
            return String(value)
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;")
                .replaceAll("'", "&#039;");
        }

        runReuseCheck();
    </script>
</body>
</html>
        """
    )