from fastapi.responses import HTMLResponse

from prototype import (
    app,
    search_documents,
)

REQUIRED_EMA_DOCUMENTS = [
    {
        "id": "clinical_study_report",
        "label": "Clinical Study Report",
        "description": "Final clinical study report for the relevant trial or study.",
        "keywords": ["clinical", "study", "report", "csr", "phase"],
    },
    {
        "id": "safety_analysis",
        "label": "Safety Analysis",
        "description": "Integrated or study-specific safety analysis.",
        "keywords": ["safety", "adverse", "events", "risk", "tolerability"],
    },
    {
        "id": "investigator_brochure",
        "label": "Investigator Brochure",
        "description": "Investigator brochure or supporting clinical background material.",
        "keywords": ["investigator", "brochure", "ib"],
    },
    {
        "id": "risk_management_plan",
        "label": "Risk Management Plan",
        "description": "Risk management documentation for regulatory submission.",
        "keywords": ["risk", "management", "plan", "rmp"],
    },
    {
        "id": "regulatory_response",
        "label": "Regulatory Response",
        "description": "Responses to EMA or authority questions.",
        "keywords": ["ema", "regulatory", "response", "submission", "authority"],
    },
]


def find_best_document_for_requirement(requirement: dict, project: str):
    scored_documents = {}

    project_terms = [
        term.lower()
        for term in project.replace("-", " ").replace("_", " ").split()
        if len(term) > 2
    ]

    for keyword in requirement["keywords"]:
        search_results = search_documents(q=keyword)

        for result in search_results:
            searchable_text = " ".join([
                str(result.get("title", "")),
                str(result.get("file_uri", "")),
                str(result.get("owner", "")),
                str(result.get("department_id", "")),
                str(result.get("source_system_id", "")),
                str(result.get("validation_status_id", "")),
                str(result.get("matching_chunks", "")),
            ]).lower()

            # Prefer documents connected to the selected project.
            project_score = sum(
                1 for term in project_terms
                if term in searchable_text
            )

            # Skip documents that do not seem related to the project at all,
            # unless no project was entered.
            if project_terms and project_score == 0:
                continue

            document_id = result["document_id"]

            if document_id not in scored_documents:
                scored_documents[document_id] = {
                    "document": result,
                    "score": 0,
                }

            scored_documents[document_id]["score"] += 1 + project_score

    if not scored_documents:
        return None

    best_match = max(
        scored_documents.values(),
        key=lambda item: item["score"],
    )["document"]

    return {
        "document_id": best_match["document_id"],
        "title": best_match["title"],
        "file_uri": best_match["file_uri"],
        "owner": best_match["owner"],
        "security_level_id": best_match["security_level_id"],
        "department_id": best_match["department_id"],
        "source_system_id": best_match["source_system_id"],
        "validation_status_id": best_match["validation_status_id"],
        "current_tokenization_id": best_match["current_tokenization_id"],
        "fake_relevance_score": best_match["fake_relevance_score"],
    }

@app.get("/regulatory/checklist", tags=["Mocks"])
def regulatory_checklist(project: str = "ALK-depot"):
    checklist_items = []

    for requirement in REQUIRED_EMA_DOCUMENTS:
        matched_document = find_best_document_for_requirement(requirement, project)

        if matched_document is None:
            status = "Missing"
        elif matched_document["validation_status_id"] != "VAL_OK":
            status = "Needs validation"
        else:
            status = "Ready"

        checklist_items.append({
            "requirement_id": requirement["id"],
            "label": requirement["label"],
            "description": requirement["description"],
            "status": status,
            "matched_document": matched_document,
        })

    ready_count = sum(1 for item in checklist_items if item["status"] == "Ready")
    missing_count = sum(1 for item in checklist_items if item["status"] == "Missing")
    needs_validation_count = sum(1 for item in checklist_items if item["status"] == "Needs validation")

    total = len(checklist_items)

    if missing_count == 0 and needs_validation_count == 0:
        overall_status = "Submission package appears complete"
    elif missing_count > 0:
        overall_status = "Submission package is incomplete"
    else:
        overall_status = "Submission package requires validation"

    return {
        "project": project,
        "overall_status": overall_status,
        "ready_count": ready_count,
        "missing_count": missing_count,
        "needs_validation_count": needs_validation_count,
        "total_requirements": total,
        "completion_percentage": round((ready_count / total) * 100),
        "checklist": checklist_items,
    }


@app.get("/regulatory-checklist", response_class=HTMLResponse, tags=["Mocks"])
def regulatory_checklist_page():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
<head>
    <title>Regulatory Submission Checklist</title>
    <style>
        :root {
            --bg: #f8f5ef;
            --panel: #fffdf8;
            --ink: #2f261d;
            --muted: #73675a;
            --border: #e7dccd;
            --gold: #b7791f;
            --gold-light: #fff4dc;
            --green: #2f855a;
            --green-light: #e6f4ea;
            --red: #c53030;
            --red-light: #fff0f0;
            --blue: #2b6cb0;
            --blue-light: #ebf4ff;
            --dark: #3b2f22;
        }

        body {
            margin: 0;
            font-family: Georgia, "Times New Roman", serif;
            background:
                radial-gradient(circle at top left, #fff8ea 0, transparent 35%),
                linear-gradient(135deg, #f8f5ef 0%, #f3efe7 100%);
            color: var(--ink);
        }

        .header {
            background: #3b2f22;
            color: white;
            padding: 28px 48px;
            border-bottom: 6px solid var(--gold);
        }

        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .seal {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            border: 2px solid #f6d365;
            display: grid;
            place-items: center;
            font-weight: bold;
            color: #f6d365;
        }

        .header h1 {
            margin: 16px 0 6px 0;
            font-size: 34px;
            letter-spacing: 0.2px;
        }

        .header p {
            margin: 0;
            color: #e9ddcc;
            font-family: Arial, sans-serif;
        }

        .container {
            max-width: 1180px;
            margin: 32px auto;
            padding: 0 24px;
        }

        .toolbar {
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 14px;
            align-items: end;
            margin-bottom: 22px;
        }

        .field {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 6px 18px rgba(59, 47, 34, 0.08);
        }

        label {
            display: block;
            font-family: Arial, sans-serif;
            font-size: 13px;
            font-weight: bold;
            color: var(--muted);
            margin-bottom: 8px;
        }

        input {
            width: 100%;
            box-sizing: border-box;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 11px 12px;
            font-size: 16px;
            color: var(--ink);
            background: white;
        }

        button {
            height: 47px;
            border: none;
            border-radius: 12px;
            padding: 0 22px;
            cursor: pointer;
            font-weight: bold;
            color: white;
            background: var(--gold);
            box-shadow: 0 6px 18px rgba(183, 121, 31, 0.25);
        }

        button:hover {
            background: #975a16;
        }

        .link-button {
            height: 47px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            padding: 0 18px;
            background: #fff;
            border: 1px solid var(--border);
            color: var(--dark);
            text-decoration: none;
            font-family: Arial, sans-serif;
            font-weight: bold;
            box-sizing: border-box;
        }

        .summary {
            display: grid;
            grid-template-columns: 1.2fr repeat(3, 0.6fr);
            gap: 18px;
            margin-bottom: 22px;
        }

        .card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 22px;
            box-shadow: 0 8px 26px rgba(59, 47, 34, 0.08);
        }

        .status-title {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .status-sub {
            font-family: Arial, sans-serif;
            color: var(--muted);
            line-height: 1.45;
        }

        .metric {
            text-align: center;
        }

        .metric-value {
            font-size: 34px;
            font-weight: bold;
        }

        .metric-label {
            font-family: Arial, sans-serif;
            color: var(--muted);
            font-size: 13px;
            margin-top: 4px;
        }

        .checklist {
            display: grid;
            gap: 14px;
        }

        .item {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 6px 20px rgba(59, 47, 34, 0.07);
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 18px;
            align-items: start;
        }

        .item h3 {
            margin: 0 0 6px 0;
            font-size: 21px;
        }

        .description {
            font-family: Arial, sans-serif;
            color: var(--muted);
            margin-bottom: 12px;
        }

        .doc {
            font-family: Arial, sans-serif;
            background: #fbf7ee;
            border: 1px solid #eadcc7;
            border-radius: 12px;
            padding: 12px;
            color: #3b2f22;
            line-height: 1.5;
        }

        .doc strong {
            color: var(--dark);
        }

        .status-pill {
            font-family: Arial, sans-serif;
            padding: 7px 12px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: bold;
            white-space: nowrap;
        }

        .ready {
            background: var(--green-light);
            color: var(--green);
        }

        .missing {
            background: var(--red-light);
            color: var(--red);
        }

        .validation {
            background: var(--blue-light);
            color: var(--blue);
        }

        .loading {
            font-family: Arial, sans-serif;
            color: var(--muted);
            padding: 20px;
        }

        .footer-note {
            margin-top: 20px;
            font-family: Arial, sans-serif;
            color: var(--muted);
            font-size: 14px;
        }
    </style>
</head>

<body>
    <div class="header">
        <div class="header-top">
            <div style="font-family: Arial, sans-serif; font-weight: bold;">ALK Regulatory Portal</div>
            <div class="seal">EMA</div>
        </div>
        <h1>Submission Readiness Checklist</h1>
        <p>
            This mock regulatory system calls the RAG Compass metadata layer to check document completeness,
            validation status, and traceability.
        </p>
    </div>

    <div class="container">
        <div class="toolbar">
            <div class="field">
                <label>Project / product search</label>
                <input id="projectInput" value="ALK-depot">
            </div>

            <button onclick="runChecklist()">Run checklist</button>

            <a class="link-button" href="/sharepoint">Upload documents</a>
        </div>

        <div id="summary" class="summary">
            <div class="card">
                <div class="status-title">Ready to check submission package</div>
                <div class="status-sub">
                    Upload a few project documents through the mock SharePoint page, then run the checklist here.
                </div>
            </div>

            <div class="card metric">
                <div class="metric-value">-</div>
                <div class="metric-label">Ready</div>
            </div>

            <div class="card metric">
                <div class="metric-value">-</div>
                <div class="metric-label">Missing</div>
            </div>

            <div class="card metric">
                <div class="metric-value">-</div>
                <div class="metric-label">Complete</div>
            </div>
        </div>

        <div id="checklist" class="checklist"></div>

        <div class="footer-note">
            The checklist does not store documents itself. It calls the shared metadata layer and checks document records,
            validation status, tokenization IDs, and source links.
        </div>
    </div>

    <script>
        async function runChecklist() {
            const project = document.getElementById("projectInput").value || "ALK-depot";
            const checklist = document.getElementById("checklist");

            checklist.innerHTML = "<div class='loading'>Calling RAG Compass metadata layer...</div>";

            await sleep(650);

            const response = await fetch("/regulatory/checklist?project=" + encodeURIComponent(project));
            const data = await response.json();

            renderSummary(data);
            renderChecklist(data);
        }

        function renderSummary(data) {
            const summary = document.getElementById("summary");

            summary.innerHTML = `
                <div class="card">
                    <div class="status-title">${escapeHtml(data.overall_status)}</div>
                    <div class="status-sub">
                        Project: <strong>${escapeHtml(data.project)}</strong><br>
                        ${data.ready_count} of ${data.total_requirements} required document categories are ready.
                    </div>
                </div>

                <div class="card metric">
                    <div class="metric-value">${data.ready_count}</div>
                    <div class="metric-label">Ready</div>
                </div>

                <div class="card metric">
                    <div class="metric-value">${data.missing_count}</div>
                    <div class="metric-label">Missing</div>
                </div>

                <div class="card metric">
                    <div class="metric-value">${data.completion_percentage}%</div>
                    <div class="metric-label">Complete</div>
                </div>
            `;
        }

        function renderChecklist(data) {
            const checklist = document.getElementById("checklist");
            let html = "";

            for (const item of data.checklist) {
                const statusClass =
                    item.status === "Ready"
                        ? "ready"
                        : item.status === "Missing"
                            ? "missing"
                            : "validation";

                html += `
                    <div class="item">
                        <div>
                            <h3>${escapeHtml(item.label)}</h3>
                            <div class="description">${escapeHtml(item.description)}</div>
                `;

                if (item.matched_document) {
                    html += `
                        <div class="doc">
                            <strong>Matched document:</strong> ${escapeHtml(item.matched_document.title)}<br>
                            <strong>Document ID:</strong> ${escapeHtml(item.matched_document.document_id)}<br>
                            <strong>Source:</strong> ${escapeHtml(item.matched_document.file_uri)}<br>
                            <strong>Owner:</strong> ${escapeHtml(item.matched_document.owner)}<br>
                            <strong>Validation:</strong> ${escapeHtml(item.matched_document.validation_status_id)}
                            · <strong>Tokenization:</strong> ${escapeHtml(item.matched_document.current_tokenization_id)}
                        </div>
                    `;
                } else {
                    html += `
                        <div class="doc">
                            No matching document was found in the metadata layer.
                        </div>
                    `;
                }

                html += `
                        </div>
                        <div>
                            <span class="status-pill ${statusClass}">${escapeHtml(item.status)}</span>
                        </div>
                    </div>
                `;
            }

            checklist.innerHTML = html;
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

        runChecklist();
    </script>
</body>
</html>
        """
    )