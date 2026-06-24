from fastapi.responses import HTMLResponse

from prototype import app


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
                <a href="/docs" style="color:#99f6e4;">API docs</a><br>
                <a href="/tables" style="color:#99f6e4;">View in-memory tables</a>
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
            updateSteps(aiMessageId, 4);

            await sleep(300);
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
                        <div class="step" data-step="3">Vectorizing prompt and comparing document chunks...</div>
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