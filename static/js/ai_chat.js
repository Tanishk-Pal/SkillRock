// SkillBot AI Assistant — ChatGPT Experience Client Script

document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("aiChatForm");
    const chatInput = document.getElementById("aiChatInput");
    const sendBtn = document.getElementById("aiSendBtn");
    const streamContainer = document.getElementById("aiChatMessages");
    const emptyWelcome = document.getElementById("emptyWelcomeState");
    const promptChips = document.querySelectorAll(".prompt-chip");
    const btnNewChat = document.getElementById("btnNewChat");

    // Markdown Formatter for clean ChatGPT-style rendering
    function formatMarkdown(text) {
        if (!text) return "";
        let escaped = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Code blocks: ```language ... ```
        escaped = escaped.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre><code>${code.trim()}</code></pre>`;
        });

        // Inline code: `code`
        escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Headers
        escaped = escaped.replace(/^### (.*$)/gim, '<h4>$1</h4>');
        escaped = escaped.replace(/^## (.*$)/gim, '<h3>$1</h3>');
        escaped = escaped.replace(/^# (.*$)/gim, '<h2>$1</h2>');

        // Bold and Italic
        escaped = escaped.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
        escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Bullet points
        escaped = escaped.replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>');
        escaped = escaped.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
        // Clean multiple nested ul tags
        escaped = escaped.replace(/<\/ul>\s*<ul>/g, '');

        // Line breaks (convert newlines that aren't inside pre blocks)
        escaped = escaped.replace(/\n\n/g, '<p></p>');
        escaped = escaped.replace(/\n/g, '<br>');

        return escaped;
    }

    // Scroll to bottom smoothly
    function scrollToBottom() {
        if (streamContainer) {
            streamContainer.scrollTop = streamContainer.scrollHeight;
        }
    }

    // Hide welcome state once chatting starts
    function hideEmptyWelcome() {
        if (emptyWelcome) {
            emptyWelcome.style.display = "none";
        }
    }

    // Append Message Row
    function appendMessageRow(sender, contentHtml) {
        hideEmptyWelcome();
        if (!streamContainer) return null;

        const row = document.createElement("div");
        row.className = `chatgpt-row ${sender}`;

        if (sender === "user") {
            const bubble = document.createElement("div");
            bubble.className = "chatgpt-bubble";
            bubble.textContent = contentHtml; // text content for safety
            row.appendChild(bubble);
        } else {
            const avatar = document.createElement("div");
            avatar.className = "chatgpt-row-avatar";
            avatar.innerHTML = "🤖";

            const bubble = document.createElement("div");
            bubble.className = "chatgpt-bubble";
            bubble.innerHTML = contentHtml;

            row.appendChild(avatar);
            row.appendChild(bubble);
        }

        streamContainer.appendChild(row);
        scrollToBottom();
        return row;
    }

    // Show ChatGPT 3-Dots Animated Thinking Indicator (Zero Blur, Zero Overlay)
    function showThinkingIndicator() {
        hideEmptyWelcome();
        if (!streamContainer) return null;

        const row = document.createElement("div");
        row.id = "chatgptThinkingRow";
        row.className = "chatgpt-row bot";
        row.innerHTML = `
            <div class="chatgpt-row-avatar">🤖</div>
            <div class="chatgpt-bubble">
                <div class="chatgpt-dots-indicator" aria-label="SkillBot is thinking...">
                    <span class="chatgpt-dot"></span>
                    <span class="chatgpt-dot"></span>
                    <span class="chatgpt-dot"></span>
                </div>
            </div>
        `;
        streamContainer.appendChild(row);
        scrollToBottom();
        return row;
    }

    // Auto-resize input textarea like ChatGPT
    function autoResizeInput() {
        if (!chatInput) return;
        chatInput.style.height = "auto";
        chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + "px";

        if (sendBtn) {
            sendBtn.disabled = !chatInput.value.trim();
        }
    }

    if (chatInput) {
        chatInput.addEventListener("input", autoResizeInput);

        // Submit on Enter, newline on Shift+Enter
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (chatInput.value.trim()) {
                    sendMessage();
                }
            }
        });
    }

    // Send Message
    async function sendMessage(presetText) {
        const text = presetText || (chatInput ? chatInput.value.trim() : "");
        if (!text) return;

        // Reset input box
        if (chatInput) {
            chatInput.value = "";
            chatInput.style.height = "auto";
            if (sendBtn) sendBtn.disabled = true;
        }

        // 1. Append User Bubble
        appendMessageRow("user", text);

        // 2. Append Thinking Indicator
        const thinkingElem = showThinkingIndicator();

        try {
            const res = await fetch("/api/ai/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({ message: text })
            });

            const data = await res.json();
            if (thinkingElem) thinkingElem.remove();

            if (data.reply) {
                const formattedHtml = formatMarkdown(data.reply);
                appendMessageRow("bot", formattedHtml);
            } else {
                appendMessageRow("bot", "<p>I could not process that request right now. Please try again or rephrase your question.</p>");
            }
        } catch (err) {
            if (thinkingElem) thinkingElem.remove();
            appendMessageRow("bot", "<p style='color: #EF4444;'>Network connection interrupted. Please verify your connection and try again.</p>");
        }

        scrollToBottom();
    }

    // Form submit listener
    if (chatForm) {
        chatForm.addEventListener("submit", (e) => {
            e.preventDefault();
            sendMessage();
        });
    }

    // Suggested prompt cards click listener
    promptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-prompt") || chip.textContent.trim();
            if (query) {
                sendMessage(query);
            }
        });
    });

    // New Chat button to reset stream
    if (btnNewChat) {
        btnNewChat.addEventListener("click", () => {
            if (streamContainer) {
                streamContainer.innerHTML = "";
                if (emptyWelcome) {
                    emptyWelcome.style.display = "block";
                    streamContainer.appendChild(emptyWelcome);
                }
            }
            if (chatInput) {
                chatInput.value = "";
                chatInput.style.height = "auto";
                chatInput.focus();
            }
            if (sendBtn) sendBtn.disabled = true;
        });
    }

    // Initial focus on input
    if (chatInput) {
        chatInput.focus();
    }

    if (window.lucide) {
        lucide.createIcons();
    }
});
