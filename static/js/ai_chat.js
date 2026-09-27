// SkillBot AI Assistant Client-side Script

document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("aiChatForm");
    const chatInput = document.getElementById("aiChatInput");
    const messagesContainer = document.getElementById("aiChatMessages");
    const promptChips = document.querySelectorAll(".prompt-chip");

    // Helper: append message bubble
    function appendMessage(sender, text, isMarkdown = false) {
        if (!messagesContainer) return;

        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${sender === "user" ? "user" : "bot"}`;
        
        const avatar = document.createElement("div");
        avatar.className = "bubble-avatar";
        avatar.innerHTML = sender === "user" ? "👤" : "🤖";

        const content = document.createElement("div");
        content.className = "bubble-body";
        
        if (sender === "bot") {
            // Simple markdown parser for bullets, headers, bold
            let formatted = text
                .replace(/^### (.*$)/gim, '<h4 style="margin: 6px 0; font-size: 0.95rem; font-weight: 600; color: #0F172A;">$1</h4>')
                .replace(/^## (.*$)/gim, '<h3 style="margin: 8px 0; font-size: 1rem; font-weight: 600; color: #0F172A;">$1</h3>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/^\* (.*$)/gim, '<li style="margin-left: 18px; margin-bottom: 2px;">$1</li>')
                .replace(/\n/g, '<br>');
            content.innerHTML = formatted;
        } else {
            content.textContent = text;
        }

        bubble.appendChild(avatar);
        bubble.appendChild(content);
        messagesContainer.appendChild(bubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Helper: show typing indicator
    function showTypingIndicator() {
        const ind = document.createElement("div");
        ind.id = "typingIndicator";
        ind.className = "chat-bubble bot";
        ind.innerHTML = `
            <div class="bubble-avatar">🤖</div>
            <div class="bubble-body" style="color: #64748B; font-style: italic;">
                SkillBot is thinking...
            </div>
        `;
        messagesContainer.appendChild(ind);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return ind;
    }

    // Handle form submit
    async function sendMessage(msgText) {
        const text = msgText || (chatInput ? chatInput.value.trim() : "");
        if (!text) return;

        if (chatInput) chatInput.value = "";
        appendMessage("user", text);

        const typingElem = showTypingIndicator();

        try {
            const res = await fetch("/api/ai/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });

            const data = await res.json();
            if (typingElem) typingElem.remove();

            if (data.reply) {
                appendMessage("bot", data.reply);
            } else {
                appendMessage("bot", "I am having trouble retrieving that skill advice. Please try again.");
            }
        } catch (err) {
            if (typingElem) typingElem.remove();
            appendMessage("bot", "Network error. Please make sure the server is reachable.");
        }
    }

    if (chatForm) {
        chatForm.addEventListener("submit", (e) => {
            e.preventDefault();
            sendMessage();
        });
    }

    promptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-prompt") || chip.textContent.trim();
            sendMessage(query);
        });
    });

    // Roadmap Generation in Assistant Tab
    const roadmapBtn = document.getElementById("btnGenerateRoadmap");
    const roadmapSkillInput = document.getElementById("roadmapSkillSelect");
    const roadmapOutput = document.getElementById("roadmapResultContainer");

    if (roadmapBtn && roadmapSkillInput && roadmapOutput) {
        roadmapBtn.addEventListener("click", async () => {
            const skill = roadmapSkillInput.value.trim();
            if (!skill) return;

            roadmapOutput.innerHTML = '<div style="color: #94a3b8; padding: 20px; text-align: center;">Curating beginner roadmap...</div>';

            try {
                const res = await fetch(`/api/ai/roadmap?skill=${encodeURIComponent(skill)}`);
                const data = await res.json();

                let stepsHtml = "";
                if (data.steps && data.steps.length) {
                    data.steps.forEach(step => {
                        stepsHtml += `<div style="padding: 10px 14px; background: rgba(255,255,255,0.04); border-left: 3px solid #06b6d4; border-radius: 6px; margin-bottom: 8px;">${step}</div>`;
                    });
                }

                roadmapOutput.innerHTML = `
                    <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <h3 style="color: #38bdf8;">${data.title}</h3>
                            <span class="skill-tag">${data.estimated_time || "4 Weeks"}</span>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.92rem; margin-bottom: 16px;">${data.description}</p>
                        <div>${stepsHtml}</div>
                    </div>
                `;
            } catch (err) {
                roadmapOutput.innerHTML = '<div style="color: #ef4444; padding: 10px;">Failed to generate roadmap.</div>';
            }
        });
    }
});
