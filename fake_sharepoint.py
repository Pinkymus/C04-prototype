from datetime import datetime
from pathlib import Path

from fastapi import UploadFile, File, Form
from fastapi.responses import HTMLResponse

from prototype import (
    app,
    FILE_TYPE_BY_EXTENSION,
    DocumentIntake,
    create_document_record,
)


@app.get("/sharepoint", response_class=HTMLResponse, tags=["Mocks"])
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

        .links {
            max-width: 1100px;
            margin: -20px auto 40px auto;
            display: flex;
            gap: 12px;
        }

        .links a {
            color: #0066cc;
            text-decoration: none;
            font-weight: bold;
        }

        .links a:hover {
            text-decoration: underline;
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
                <option value="SEC02">SEC02 - Internal</option>
                <option value="SEC03">SEC03 - Restricted</option>
                <option value="SEC04">SEC04 - Highly Restricted</option>
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

    <div class="links">
        <a href="/ai">Open mock internal AI</a>
        <a href="/docs">Open API docs</a>
        <a href="/tables">View all in-memory tables</a>
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
            html += "<tr><th>document_id</th><th>title</th><th>file_type</th><th>security</th><th>source</th><th>owner</th><th>tokenization</th><th>status</th></tr>";

            for (const doc of documents) {
                html += "<tr>";
                html += "<td>" + escapeHtml(doc.document_id) + "</td>";
                html += "<td>" + escapeHtml(doc.title) + "</td>";
                html += "<td>" + escapeHtml(doc.file_type_id) + "</td>";
                html += "<td>" + escapeHtml(doc.security_level_id) + "</td>";
                html += "<td>" + escapeHtml(doc.source_system_id) + "</td>";
                html += "<td>" + escapeHtml(doc.owner) + "</td>";
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


@app.post("/mock-sharepoint/upload", tags=["Mocks"])
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
            f"Document owner is {owner}. Department is {department_id}. Source system is {source_system_id}."
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