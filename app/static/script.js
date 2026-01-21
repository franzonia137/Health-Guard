const API_URL = "";
const USER_ID = "web_user_" + Math.random().toString(36).substr(2, 9);
const SESSION_ID = "session_" + Date.now();

const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function useSuggestion(text) {
    userInput.value = text;
    userInput.focus();
}

function appendMessage(text, type, data = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;

    let contentHtml = `<div class="msg-content">${text.replace(/\n/g, '<br>')}</div>`;

    // Detailed Agent Response Rendering
    if (type === 'agent' && data) {
        // Verdict Badge
        let verdictClass = 'v-neutral';
        if (data.verdict === 'True') verdictClass = 'v-true';
        if (data.verdict === 'False') verdictClass = 'v-false';

        contentHtml = `
        <div class="verdict-badge ${verdictClass}"><span class="material-icons-round">verified</span> ${data.verdict.toUpperCase()}</div>
        <div class="reasoning-box"><strong>Analysis:</strong> ${data.reasoning_trace}</div>
        <div class="msg-content">${text}</div>
        `;

        // Evidence Table
        if (data.evidence && data.evidence.length > 0) {
            contentHtml += `<div class="evidence-box"><div class="evidence-title">Retrieval Evidence</div>`;
            data.evidence.forEach(item => {
                let icon = 'help_outline';
                let colorClass = 'neutral';

                if (item.type === 'fact') { icon = 'verified'; colorClass = 'fact'; }
                if (item.type === 'misinformation') { icon = 'warning'; colorClass = 'misinfo'; }
                if (item.type === 'image') { icon = 'image'; colorClass = 'image'; }

                const score = Math.round(item.score * 100);

                contentHtml += `
                <div class="evidence-row ${colorClass}">
                    <span class="material-icons-round type-icon">${icon}</span>
                    <span class="ev-text">${item.content.substring(0, 80)}...</span>
                    <span class="evidence-score">${score}%</span>
                </div>`;
            });
            contentHtml += `</div>`;
        }

        // Recommendations
        if (data.recommendations && data.recommendations.length > 0) {
            contentHtml += `<div class="rec-box"><div class="rec-title">Next Steps</div><ul>`;
            data.recommendations.forEach(rec => {
                contentHtml += `<li>${rec}</li>`;
            });
            contentHtml += `</ul></div>`;
        }
    }

    // Wrap agent messages in the card container for styling
    if (type === 'agent') {
        contentHtml = `<div class="agent-card">${contentHtml}</div>`;
    }

    msgDiv.innerHTML = contentHtml;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    userInput.value = '';
    userInput.disabled = true;

    const loadingId = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message agent';
    loadingDiv.id = loadingId;
    loadingDiv.innerHTML = `<em>Cross-referencing medical database...</em>`;
    chatHistory.appendChild(loadingDiv);

    try {
        const response = await fetch(`${API_URL}/agent/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: USER_ID,
                session_id: SESSION_ID,
                query: text
            })
        });

        const data = await response.json();
        document.getElementById(loadingId).remove();
        appendMessage(data.final_answer, 'agent', data);

    } catch (error) {
        document.getElementById(loadingId).remove();
        appendMessage("⚠️ Connection Error. Ensure the backend API is running.", 'agent');
        console.error(error);
    }

    userInput.disabled = false;
    userInput.focus();
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

setTimeout(() => {
    appendMessage("Welcome to **HealthGuard AI**.\nI verify medical claims using trusted data. Ask me anything!", 'agent');
}, 500);
