# RAG Compass

This is a small FastAPI prototype for demonstrating a shared metadata and RAG-readiness layer.

The prototype shows how different systems can interact with the same underlying metadata layer:

* A mock SharePoint upload page can send files into the system.
* A mock internal AI assistant can query documents using simplified RAG retrieval.
* A regulatory checklist can check whether required submission documents exist.
* A research reuse checker can combine traditional metadata search and RAG-style retrieval to detect reusable previous work.

The project uses an in-memory database, so uploaded files disappear when the server restarts. Some seed data is loaded automatically on startup for easier demo use.

---

## Project structure

```text
C04-PROTOTYPE/
│
├── prototype.py                    # Core metadata layer, search, intake, and baby RAG retrieval
├── fake_sharepoint.py              # Mock SharePoint upload system
├── fake_internal_ai.py             # Mock internal AI assistant UI
├── fake_regulatory_checklist.py    # Mock regulatory checklist
├── fake_reuse_checker.py           # Mock research reuse checker
├── requirements.txt
├── .gitignore
└── showcase_files/                 # Optional demo files
```

---

## Setup using PowerShell

Open PowerShell in the project folder.

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

When the virtual environment is active, the terminal should show:

```text
(.venv)
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Run the server

```powershell
python -m uvicorn prototype:app --reload
```

The app should now run at:

```text
http://127.0.0.1:8000
```

---

## Setup using Git Bash / Bash

Open Git Bash or Bash in the project folder.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

```bash
source .venv/Scripts/activate
```

On macOS/Linux, the activation path is usually:

```bash
source .venv/bin/activate
```

When the virtual environment is active, the terminal should show:

```text
(.venv)
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the server

```bash
python -m uvicorn prototype:app --reload
```

The app should now run at:

```text
http://127.0.0.1:8000
```

---

## Pages to open

After starting the server, open these pages in the browser:

### Mock SharePoint upload

```text
http://127.0.0.1:8000/sharepoint
```

Used to upload files into the metadata layer.

### Mock internal AI assistant

```text
http://127.0.0.1:8000/ai
```

Used to query documents through the simplified RAG retrieval endpoint.

### Regulatory checklist

```text
http://127.0.0.1:8000/regulatory-checklist
```

Used to check whether required regulatory submission documents are present, validated, and traceable.

### Research reuse checker

```text
http://127.0.0.1:8000/reuse-checker
```

Used to check whether a new research idea overlaps with previous work. This page combines traditional metadata search and simplified RAG-style retrieval.

### Swagger API documentation

```text
http://127.0.0.1:8000/docs
```

Shows all API endpoints grouped by prototype routes and mock system routes.

### In-memory database tables

```text
http://127.0.0.1:8000/tables
```

Shows the current in-memory records for documents, tokenization's, chunks, and fake embeddings.

---

## Main API routes

### Core metadata layer

```text
GET  /
POST /documents/intake
GET  /documents
GET  /documents/{document_id}
GET  /documents/{document_id}/tokenization
GET  /tables
```

### Traditional search

```text
GET /search
```

Searches across document records, metadata, and document chunks.

Example:

```text
http://127.0.0.1:8000/search?q=safety
```

### Simplified RAG retrieval

```text
POST /rag-compass/query
```

Uses a simplified RAG-style retrieval method with TF-IDF vectorization and cosine similarity.

This simulates the retrieval part of a RAG system:

1. Check user access level.
2. Collect accessible document chunks.
3. Vectorize chunks and prompt using TF-IDF.
4. Compare the prompt against document chunks.
5. Return matching source documents and chunks.

In a real implementation, TF-IDF would be replaced by embeddings and a vector database.

---

## Demo flow

A simple demo flow is:

1. Start the server.
2. Open the mock SharePoint page.
3. Upload a few `.txt` files.
4. Open the internal AI assistant and ask a question.
5. Open the regulatory checklist and check an ALK-depot package.
6. Open the research reuse checker and test whether an idea overlaps with existing work.
7. Open Swagger to show that the mock systems call into the shared prototype layer.

The app also creates some demo documents automatically on startup, so the pages can be shown even before uploading new files.

---

## Example AI prompts

Try these in the internal AI assistant:

```text
Find documents about ALK-depot safety and adverse events.
```

```text
What do we know about dose escalation?
```

```text
Find regulatory documents for EMA submission.
```

```text
Do we have anything about pediatric allergen immunotherapy?
```

---

## Example reuse checker prompt

Try this in the research reuse checker:

```text
Pediatric allergen immunotherapy adherence study with focus on symptom reduction, long-term outcomes, and safety monitoring
```

---

## Example test file content

You can create a `.txt` file and upload it through the mock SharePoint page.

Example filename:

```text
Pediatric-AIT-study-overview.txt
```

Example content:

```text
This study overview describes pediatric allergen immunotherapy research.
The study focuses on children and adolescents, treatment adherence, symptom reduction, long-term outcomes, and safety monitoring during allergy treatment.
The work includes observations from previous clinical development projects and may be reused when designing future pediatric AIT studies.
```

---

## Updating requirements.txt

If new packages are installed, update `requirements.txt` with:

### PowerShell

```powershell
python -m pip freeze > requirements.txt
```

### Bash

```bash
python -m pip freeze > requirements.txt
```

---

## Notes

This is a prototype, not a production system.

The current version uses:

* FastAPI for the backend
* In-memory Python dictionaries instead of a real database
* Fake embedding records to mirror the proposed database structure
* TF-IDF and cosine similarity as a simplified RAG retrieval method
* Mock frontend pages to demonstrate how different systems could call the same metadata layer

The goal is to demonstrate the concept, not to implement a full enterprise-ready data platform.
