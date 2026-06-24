from datetime import datetime
from pathlib import Path
from uuid import uuid4
import random
import html

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


app = FastAPI(title="ALK Metadata + RAG Readiness Prototype")


DOCUMENTS = {}
TOKENIZED_DOCUMENTS = {}
DOCUMENT_CHUNKS = {}
CHUNK_EMBEDDINGS = {}


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

        if start >= len(tokens):
            break

    return chunks


def create_document_record(document: DocumentIntake):
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
            "note": "Prototype tokenizer. Real system would use model-specific tokenization.",
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


@app.get("/sharepoint", response_class=HTMLResponse)
def fake_sharepoint_page():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
<head>
    <title>Mock SharePoint Intake</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f8fc;
            color: #071b4d;
        }

        .topbar {
            background: #001f4d;
            color: white;
            padding: 18px 32px;
            font-size: 24px;
            font-weight: bold;
        }

        .container {
            max-width: 1100px;
            margin: 40px auto;
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 24px;
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 28px;
            box-shadow: 0 8px 24px rgba(0, 31, 77, 0.12);
        }

        h1, h2 {
            margin-top: 0;
        }

        .subtitle {
            color: #4b5f84;
            margin-bottom: 24px;
        }

        .dropzone {
            border: 2px dashed #7fa8df;
            border-radius: 16px;
            padding: 50px;
            text-align: center;
            background: #f8fbff;
            cursor: pointer;
            transition: 0.2s;
        }

        .dropzone:hover {
            background: #eef6ff;
        }

        .dropzone.dragover {
            background: #e1f5f2;
            border-color: #00a99d;
        }

        .button {
            margin-top: 18px;
            background: #0066cc;
            color: white;
            border: none;
            padding: 12px 22px;
            border-radius: 8px;
            font-size: 15px;
            cursor: pointer;
        }

        .button:hover {
            background: #004f9e;
        }

        label {
            display: block;
            margin-top: 14px;
            font-weight: bold;
            font-size: 14px;
        }

        select, input {
            width: 100%;
            box-sizing: border-box;
            padding: 10px;
            margin-top: 6px;
            border: 1px solid #ccd7e6;
            border-radius: 8px;
        }

        .status {
            margin-top: 20px;
            padding: 14px;
            border-radius: 10px;
            background: #eef6ff;
            white-space: pre-wrap;
            font-family: Consolas, monospace;
            font-size: 13px;
        }

        .success {
            background: #e6f7f3;
            color: #006b60;
        }

        .error {
            background: #ffecec;
            color: #990000;
        }

        .records {
            max-width: 1100px;
            margin: 0 auto 40px auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th, td {
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background: #eef4fb;
        }

        .pill {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 999px;
            background: #dff5f0;
            color: #00796b;
            font-weight: bold;
            font-size: 12px;
        }
    </style>
</head>

<body>
    <div class="topbar">ALK Mock SharePoint Intake</div>

    <div class="container">
        <div class="card">
            <h1>Upload to RAG-ready metadata layer</h1>
            <p class="subtitle">
                This simulates a SharePoint or Microsoft 365 source sending a file into the intake pipeline.
            </p>

            <div id="dropzone" class="dropzone">
                <h2>Drag & drop file here</h2>
                <p>or choose a file manually</p>
                <button class="button" onclick="document.getElementById('fileInput').click()">Choose file</button>
                <input id="fileInput" type="file" hidden>
            </div>

            <div id="status" class="status">No file uploaded yet.</div>
        </div>

        <div class="card">
            <h2>Metadata defaults</h2>

            <label>Department</label>
            <select id="department">
                <option value="DEP_CLIN">Clinical Development</option>
                <option value="DEP_REG">Regulatory Affairs</option>
                <option value="DEP_SAFETY">Safety</option>
                <option value="DEP_RND">R&D</option>
            </select>

            <label>Security level</label>
            <select id="security">
                <option value="SEC02">Internal</option>
                <option value="SEC03">Restricted</option>
                <option value="SEC04">Highly Restricted</option>
            </select>

            <label>Owner</label>
            <input id="owner" value="Sarah Green">

            <label>Source system</label>
            <select id="source">
                <option value="SRC_SP01">SharePoint</option>
                <option value="SRC_OD01">OneDrive</option>
                <option value="SRC_TEAMS01">Teams</option>
                <option value="SRC_MANUAL">Manual Upload</option>
            </select>

            <p class="subtitle" style="margin-top: 20px;">
                The prototype extracts filename and extension automatically, then creates document, tokenization, chunk, and fake embedding records.
            </p>
        </div>
    </div>

    <div class="records card">
        <h2>Current in-memory DOCUMENT records</h2>
        <div id="recordsTable">No records yet.</div>
    </div>

    <script>
        const dropzone = document.getElementById("dropzone");
        const fileInput = document.getElementById("fileInput");
        const statusBox = document.getElementById("status");

        dropzone.addEventListener("dragover", (event) => {
            event.preventDefault();
            dropzone.classList.add("dragover");
        });

        dropzone.addEventListener("dragleave", () => {
            dropzone.classList.remove("dragover");
        });

        dropzone.addEventListener("drop", async (event) => {
            event.preventDefault();
            dropzone.classList.remove("dragover");

            const file = event.dataTransfer.files[0];
            if (file) {
                await uploadFile(file);
            }
        });

        fileInput.addEventListener("change", async () => {
            const file = fileInput.files[0];
            if (file) {
                await uploadFile(file);
            }
        });

        async function uploadFile(file) {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("department_id", document.getElementById("department").value);
            formData.append("security_level_id", document.getElementById("security").value);
            formData.append("owner", document.getElementById("owner").value);
            formData.append("source_system_id", document.getElementById("source").value);

            statusBox.className = "status";
            statusBox.textContent = "Uploading and processing " + file.name + "...";

            try {
                const response = await fetch("/mock-sharepoint/upload", {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(JSON.stringify(result, null, 2));
                }

                statusBox.className = "status success";
                statusBox.textContent =
                    "Upload complete!\\n\\n" +
                    "Document ID: " + result.document_id + "\\n" +
                    "Tokenization ID: " + result.tokenization_id + "\\n" +
                    "Chunks created: " + result.chunks_created + "\\n" +
                    "Status: " + result.status;

                await refreshRecords();
            } catch (error) {
                statusBox.className = "status error";
                statusBox.textContent = "Upload failed:\\n" + error.message;
            }
        }

        async function refreshRecords() {
            const response = await fetch("/documents");
            const documents = await response.json();

            if (documents.length === 0) {
                document.getElementById("recordsTable").textContent = "No records yet.";
                return;
            }

            let html = "<table>";
            html += "<tr><th>document_id</th><th>title</th><th>file_type</th><th>security</th><th>source</th><th>tokenization</th><th>status</th></tr>";

            for (const doc of documents) {
                html += "<tr>";
                html += "<td>" + escapeHtml(doc.document_id) + "</td>";
                html += "<td>" + escapeHtml(doc.title) + "</td>";
                html += "<td>" + escapeHtml(doc.file_type_id) + "</td>";
                html += "<td>" + escapeHtml(doc.security_level_id) + "</td>";
                html += "<td>" + escapeHtml(doc.source_system_id) + "</td>";
                html += "<td>" + escapeHtml(doc.current_tokenization_id) + "</td>";
                html += "<td><span class='pill'>RAG-ready</span></td>";
                html += "</tr>";
            }

            html += "</table>";
            document.getElementById("recordsTable").innerHTML = html;
        }

        function escapeHtml(value) {
            return String(value)
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;")
                .replaceAll("'", "&#039;");
        }

        refreshRecords();
    </script>
</body>
</html>
        """
    )


@app.post("/mock-sharepoint/upload")
async def mock_sharepoint_upload(
    file: UploadFile = File(...),
    department_id: str = Form("DEP_CLIN"),
    security_level_id: str = Form("SEC02"),
    owner: str = Form("Sarah Green"),
    source_system_id: str = Form("SRC_SP01"),
):
    filename = file.filename or "unknown_file"
    suffix = Path(filename).suffix.lower()
    file_type_id = FILE_TYPE_BY_EXTENSION.get(suffix, "FT_UNKNOWN")

    raw_content = await file.read()

    try:
        text_content = raw_content.decode("utf-8")
    except UnicodeDecodeError:
        text_content = ""

    if not text_content.strip():
        text_content = (
            f"Prototype extracted metadata from file {filename}. "
            f"The real system would extract text from {suffix or 'unknown'} files using OCR, parsers, "
            f"or document processing services. "
            f"This placeholder content is used to demonstrate tokenization, chunking, and embedding creation. "
            f"Document owner is {owner}. Department is {department_id}. Source system is {source_system_id}. "
        )

    title = Path(filename).stem.replace("_", " ").replace("-", " ").title()

    intake = DocumentIntake(
        title=title,
        file_uri=f"/mock-sharepoint/{filename}",
        file_type_id=file_type_id,
        security_level_id=security_level_id,
        department_id=department_id,
        source_system_id=source_system_id,
        validation_status_id="VAL_OK",
        owner=owner,
        text_content=text_content,
        extra_metadata={
            "original_filename": filename,
            "extension": suffix,
            "file_size_bytes": len(raw_content),
            "intake_source": "mock-sharepoint-upload",
            "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        },
    )

    return create_document_record(intake)


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
                "fake_relevance_score": f"{random.randint(82, 97)}%",
            })

    return results


@app.get("/ai", response_class=HTMLResponse)
def fake_internal_ai_page():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
<head>
    <title>Mock Internal AI Assistant</title>
    <style>
        :root {
            --bg: #f7f7f5;
            --panel: #ffffff;
            --text: #1f2933;
            --muted: #6b7280;
            --border: #e5e7eb;
            --accent: #0f766e;
            --accent-light: #e6f7f3;
            --dark: #111827;
        }

        body {
            margin: 0;
            font-family: Inter, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
        }

        .layout {
            height: 100vh;
            display: grid;
            grid-template-columns: 270px 1fr;
        }

        .sidebar {
            background: #202123;
            color: white;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }

        .brand {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 24px;
        }

        .new-chat {
            border: 1px solid #555;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 24px;
            cursor: pointer;
            color: #f3f4f6;
        }

        .side-item {
            padding: 10px 8px;
            border-radius: 8px;
            color: #d1d5db;
            font-size: 14px;
        }

        .side-item.active {
            background: #343541;
            color: white;
        }

        .side-bottom {
            margin-top: auto;
            font-size: 13px;
            color: #9ca3af;
            line-height: 1.5;
        }

        .main {
            display: grid;
            grid-template-rows: auto 1fr auto;
            height: 100vh;
        }

        .topbar {
            padding: 18px 32px;
            border-bottom: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.85);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .model-title {
            font-weight: 700;
            font-size: 18px;
        }

        .badge {
            display: inline-block;
            background: var(--accent-light);
            color: var(--accent);
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 700;
        }

        .chat {
            overflow-y: auto;
            padding: 32px;
        }

        .message {
            max-width: 850px;
            margin: 0 auto 24px auto;
            display: grid;
            grid-template-columns: 42px 1fr;
            gap: 14px;
        }

        .avatar {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            font-weight: bold;
            font-size: 14px;
        }

        .avatar.user {
            background: #dbeafe;
            color: #1d4ed8;
        }

        .avatar.ai {
            background: #d1fae5;
            color: #047857;
        }

        .bubble {
            background: transparent;
            line-height: 1.55;
            font-size: 15px;
        }

        .bubble.user-bubble {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 16px;
        }

        .steps {
            margin-top: 14px;
            display: grid;
            gap: 8px;
        }

        .step {
            background: white;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 12px;
            color: var(--muted);
            font-size: 14px;
        }

        .step.done {
            border-color: #99f6e4;
            background: #f0fdfa;
            color: #0f766e;
        }

        .answer-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 18px;
            margin-top: 12px;
        }

        .answer-card strong {
            color: var(--dark);
        }

        .sources-title {
            margin-top: 22px;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .source-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
            margin-bottom: 12px;
        }

        .source-card h3 {
            margin: 8px 0 6px 0;
            font-size: 16px;
        }

        .source-meta {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.45;
        }

        .pill {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 999px;
            background: #ecfdf5;
            color: #047857;
            font-weight: 700;
            font-size: 12px;
            margin-right: 6px;
        }

        .pill.security {
            background: #eff6ff;
            color: #1d4ed8;
        }

        .chunk {
            margin-top: 10px;
            background: #f9fafb;
            border-left: 3px solid var(--accent);
            padding: 10px 12px;
            border-radius: 8px;
            color: #374151;
            font-size: 13px;
        }

        .composer-wrap {
            padding: 18px 32px 28px 32px;
            background: linear-gradient(to top, var(--bg) 80%, rgba(247,247,245,0));
        }

        .composer {
            max-width: 850px;
            margin: 0 auto;
            background: white;
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: 0 8px 28px rgba(0,0,0,0.08);
            padding: 14px;
        }

        textarea {
            width: 100%;
            min-height: 72px;
            border: none;
            outline: none;
            resize: none;
            font-size: 15px;
            font-family: inherit;
            color: var(--text);
        }

        .composer-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border);
            padding-top: 12px;
            margin-top: 8px;
        }

        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        select, input {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 10px;
            background: #fafafa;
            color: var(--text);
        }

        button {
            background: var(--dark);
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 700;
        }

        button:hover {
            background: #374151;
        }

        .link {
            color: #0f766e;
            text-decoration: none;
            font-size: 14px;
            font-weight: 700;
        }

        .empty {
            max-width: 760px;
            margin: 80px auto 0 auto;
            text-align: center;
            color: var(--muted);
        }

        .empty h1 {
            color: var(--dark);
            font-size: 34px;
            margin-bottom: 8px;
        }
    </style>
</head>

<body>
    <div class="layout">
        <aside class="sidebar">
            <div class="brand">ALK Internal AI</div>
            <div class="new-chat">+ New research query</div>
            <div class="side-item active">RAG Compass Assistant</div>
            <div class="side-item">Clinical study questions</div>
            <div class="side-item">Regulatory document search</div>
            <div class="side-item">Safety data summaries</div>

            <div class="side-bottom">
                Connected to:<br>
                <strong>RAG Compass API</strong><br><br>
                <a href="/sharepoint" style="color:#99f6e4;">Mock SharePoint upload</a><br>
                <a href="/docs" style="color:#99f6e4;">API docs</a>
            </div>
        </aside>

        <main class="main">
            <div class="topbar">
                <div class="model-title">RAG Compass Assistant</div>
                <div>
                    <span class="badge">Access-controlled retrieval</span>
                </div>
            </div>

            <div id="chat" class="chat">
                <div class="empty" id="emptyState">
                    <h1>Ask across ALK knowledge</h1>
                    <p>
                        This mock AI system sends questions to the separate RAG Compass prototype.
                        It only returns documents the selected user has access to.
                    </p>
                </div>
            </div>

            <div class="composer-wrap">
                <div class="composer">
                    <textarea id="prompt">Find documents about ALK-depot clinical study safety</textarea>

                    <div class="composer-footer">
                        <div class="controls">
                            <input id="userName" value="Sarah Green">
                            <select id="clearance">
                                <option value="SEC02">SEC02 Internal</option>
                                <option value="SEC03" selected>SEC03 Restricted</option>
                                <option value="SEC04">SEC04 Highly Restricted</option>
                            </select>
                        </div>

                        <button onclick="askCompass()">Ask</button>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        async function askCompass() {
            const chat = document.getElementById("chat");
            const empty = document.getElementById("emptyState");
            if (empty) empty.remove();

            const prompt = document.getElementById("prompt").value;
            const userName = document.getElementById("userName").value;
            const clearance = document.getElementById("clearance").value;

            addUserMessage(prompt, userName);
            const aiMessageId = addAIThinkingMessage();

            await sleep(650);
            updateSteps(aiMessageId, 1);

            await sleep(700);
            updateSteps(aiMessageId, 2);

            await sleep(850);
            updateSteps(aiMessageId, 3);

            const payload = {
                prompt: prompt,
                user_name: userName,
                user_security_clearance: clearance,
                max_results: 2
            };

            const response = await fetch("/rag-compass/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            await sleep(500);
            renderAIResult(aiMessageId, result);

            chat.scrollTop = chat.scrollHeight;
        }

        function addUserMessage(prompt, userName) {
            const chat = document.getElementById("chat");

            const wrapper = document.createElement("div");
            wrapper.className = "message";
            wrapper.innerHTML = `
                <div class="avatar user">${escapeHtml(initials(userName))}</div>
                <div class="bubble user-bubble">
                    <strong>${escapeHtml(userName)}</strong><br>
                    ${escapeHtml(prompt)}
                </div>
            `;

            chat.appendChild(wrapper);
            chat.scrollTop = chat.scrollHeight;
        }

        function addAIThinkingMessage() {
            const chat = document.getElementById("chat");
            const id = "ai-" + Math.random().toString(16).slice(2);

            const wrapper = document.createElement("div");
            wrapper.className = "message";
            wrapper.id = id;
            wrapper.innerHTML = `
                <div class="avatar ai">AI</div>
                <div class="bubble">
                    <strong>RAG Compass Assistant</strong>
                    <div class="steps">
                        <div class="step" data-step="1">Calling RAG Compass API...</div>
                        <div class="step" data-step="2">Checking access rights...</div>
                        <div class="step" data-step="3">Searching metadata and tokenized chunks...</div>
                        <div class="step" data-step="4">Preparing answer with source references...</div>
                    </div>
                </div>
            `;

            chat.appendChild(wrapper);
            chat.scrollTop = chat.scrollHeight;

            return id;
        }

        function updateSteps(messageId, stepNumber) {
            const message = document.getElementById(messageId);
            const steps = message.querySelectorAll(".step");

            for (const step of steps) {
                const n = Number(step.dataset.step);
                if (n <= stepNumber) {
                    step.classList.add("done");
                    if (!step.textContent.startsWith("✓")) {
                        step.textContent = "✓ " + step.textContent;
                    }
                }
            }

            document.getElementById("chat").scrollTop = document.getElementById("chat").scrollHeight;
        }

        function renderAIResult(messageId, result) {
            const message = document.getElementById(messageId);
            const bubble = message.querySelector(".bubble");

            let html = `
                <strong>RAG Compass Assistant</strong>
                <div class="answer-card">
                    <strong>Answer</strong><br>
                    ${escapeHtml(result.answer)}
                </div>
            `;

            if (!result.results || result.results.length === 0) {
                html += `<p>No accessible documents were returned.</p>`;
                bubble.innerHTML = html;
                return;
            }

            html += `<div class="sources-title">Retrieved source documents</div>`;

            for (const doc of result.results) {
                html += `
                    <div class="source-card">
                        <span class="pill">${escapeHtml(doc.fake_relevance_score)}% relevance</span>
                        <span class="pill security">${escapeHtml(doc.security_level_id)}</span>
                        <h3>${escapeHtml(doc.title)}</h3>
                        <div class="source-meta">
                            Document ID: ${escapeHtml(doc.document_id)}<br>
                            Source URI: ${escapeHtml(doc.file_uri)}<br>
                            Tokenization: ${escapeHtml(doc.current_tokenization_id)}
                        </div>
                `;

                if (doc.matching_chunks && doc.matching_chunks.length > 0) {
                    html += `
                        <div class="chunk">
                            <strong>Matching chunk</strong><br>
                            ${escapeHtml(truncate(doc.matching_chunks[0].chunk_text, 300))}
                        </div>
                    `;
                }

                html += `</div>`;
            }

            bubble.innerHTML = html;
        }

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        function truncate(text, maxLength) {
            if (!text) return "";
            if (text.length <= maxLength) return text;
            return text.slice(0, maxLength) + "...";
        }

        function initials(name) {
            return name
                .split(" ")
                .filter(Boolean)
                .map(part => part[0])
                .join("")
                .slice(0, 2)
                .toUpperCase();
        }

        function escapeHtml(value) {
            return String(value)
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;")
                .replaceAll('"', "&quot;")
                .replaceAll("'", "&#039;");
        }
    </script>
</body>
</html>
        """
    )


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