// dashboard/static/chat.js
// Floating AI chat widget (bubble + popup) integrated with Gemini API

(function() {
    function ensureTailwind() {
        const hasTailwind = Array.from(document.styleSheets).some(s => (s.href || '').includes('tailwind')) ||
            Array.from(document.querySelectorAll('link[rel="stylesheet"]')).some(l => (l.href || '').includes('tailwind'));
        if (!hasTailwind) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.16/tailwind.min.css';
            document.head.appendChild(link);
        }
    }

    function injectStyles() {
        const style = document.createElement('style');
        style.innerHTML = `
        .hidden { display: none; }
        #chat-widget-container { position: fixed; bottom: 20px; right: 20px; display: flex; flex-direction: column; z-index: 1000; }
        #chat-popup { height: 70vh; max-height: 70vh; transition: all 0.3s; overflow: hidden; }
        @media (max-width: 768px) {
            #chat-popup { position: fixed; top: 0; right: 0; bottom: 0; left: 0; width: 100%; height: 100%; max-height: 100%; border-radius: 0; }
        }
        `;
        document.head.appendChild(style);
    }

    function buildWidget() {
        const container = document.createElement('div');
        container.id = 'chat-widget-container';
        document.body.appendChild(container);

        container.innerHTML = `
        <div id="chat-bubble" class="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center cursor-pointer text-3xl shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
        </div>
        <div id="chat-popup" class="hidden absolute bottom-20 right-0 w-96 bg-white rounded-md shadow-2xl flex flex-col transition-all text-sm">
            <div id="chat-header" class="flex justify-between items-center p-4 bg-gray-800 text-white rounded-t-md">
                <h3 class="m-0 text-lg">AquaSavvy Assistant</h3>
                <button id="close-popup" class="bg-transparent border-none text-white cursor-pointer">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="px-4 pt-3 pb-1 bg-gray-50 border-b border-gray-200 text-xs text-gray-700">
                <div><strong>Tip:</strong> Ask about features, safety (SSR, 240V), or pricing.</div>
                <div class="flex flex-wrap gap-2 mt-2">
                    <button data-q="What does AquaSavvy do?" class="text-xs bg-white border border-gray-300 rounded px-2 py-1 hover:bg-gray-100">What does AquaSavvy do?</button>
                    <button data-q="Is the pump protected from dry-run?" class="text-xs bg-white border border-gray-300 rounded px-2 py-1 hover:bg-gray-100">Dry-run protection?</button>
                    <button data-q="What is the estimated price and profit?" class="text-xs bg-white border border-gray-300 rounded px-2 py-1 hover:bg-gray-100">Price & profit</button>
                </div>
            </div>
            <div id="chat-messages" class="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-50"></div>
            <div id="chat-input-container" class="p-4 border-t border-gray-200 bg-white">
                <div class="flex space-x-2 items-center">
                    <input type="text" id="chat-input" class="flex-1 border border-gray-300 rounded-md px-3 py-2 outline-none" placeholder="Ask about AquaSavvy...">
                    <button id="chat-submit" class="bg-gray-800 text-white rounded-md px-4 py-2 cursor-pointer">Send</button>
                </div>
                <div class="text-[10px] text-center text-gray-500 pt-2">Powered by Gemini</div>
            </div>
        </div>`;

        return {
            chatInput: container.querySelector('#chat-input'),
            chatSubmit: container.querySelector('#chat-submit'),
            chatMessages: container.querySelector('#chat-messages'),
            chatBubble: container.querySelector('#chat-bubble'),
            chatPopup: container.querySelector('#chat-popup'),
            closePopup: container.querySelector('#close-popup')
        };
    }

    async function sendToGemini(userText, setLoading) {
        // Use page-defined apiUrl if available; else allow env fallback via data attribute (not provided here)
        const apiUrl = (typeof window.apiUrl !== 'undefined') ? window.apiUrl : null;
        if (!apiUrl) {
            setLoading(false);
            return { error: 'Gemini API URL not configured.' };
        }

        const systemPrompt = "You are AquaSavvy Assistant. Be concise and friendly. If users ask about AquaSavvy, summarize: dual-tank automation, dry-run protection via ACS712, ESP32, AWS IoT Core, Django web app. Provide practical steps, pricing context (BOM ~KES 6,880; est. price KES 18k–25k), and safety notes (SSR-40DA, 240V best practices). Avoid legal claims; suggest CE/UL guidance for consumer mains products.";

        const payload = {
            contents: [{ parts: [{ text: userText }]}],
            systemInstruction: { parts: [{ text: systemPrompt }] }
        };

        try {
            const resp = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            const text = data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts[0] && data.candidates[0].content.parts[0].text;
            return { text: text || 'Sorry, no response received.' };
        } catch (e) {
            return { error: `Network error: ${e.message}` };
        } finally {
            setLoading(false);
        }
    }

    function appendUserMessage(container, text) {
        const wrap = document.createElement('div');
        wrap.className = 'flex justify-end';
        wrap.innerHTML = `<div class="bg-gray-800 text-white rounded-lg py-2 px-3 max-w-[70%]">${escapeHtml(text)}</div>`;
        container.appendChild(wrap);
        container.scrollTop = container.scrollHeight;
    }

    function appendAiMessage(container, text) {
        const wrap = document.createElement('div');
        wrap.className = 'flex';
        wrap.innerHTML = `<div class="bg-white border border-gray-200 text-gray-900 rounded-lg py-2 px-3 max-w-[70%] whitespace-pre-wrap">${escapeHtml(text)}</div>`;
        container.appendChild(wrap);
        container.scrollTop = container.scrollHeight;
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function init() {
        ensureTailwind();
        injectStyles();
        const refs = buildWidget();

        function togglePopup() {
            refs.chatPopup.classList.toggle('hidden');
            if (!refs.chatPopup.classList.contains('hidden')) {
                refs.chatInput.focus();
            }
        }

        function setLoading(isLoading) {
            refs.chatSubmit.disabled = isLoading;
            refs.chatSubmit.textContent = isLoading ? '...' : 'Send';
        }

        refs.chatBubble.addEventListener('click', togglePopup);
        refs.closePopup.addEventListener('click', togglePopup);
        refs.chatSubmit.addEventListener('click', async function() {
            const text = refs.chatInput.value.trim();
            if (!text) return;
            appendUserMessage(refs.chatMessages, text);
            refs.chatInput.value = '';
            setLoading(true);
            const res = await sendToGemini(text, setLoading);
            if (res.error) {
                appendAiMessage(refs.chatMessages, `⚠️ ${res.error}`);
            } else {
                appendAiMessage(refs.chatMessages, res.text);
            }
        });
        // Quick suggestion buttons
        document.querySelectorAll('#chat-popup [data-q]').forEach(function(btn) {
            btn.addEventListener('click', function() {
                refs.chatInput.value = this.getAttribute('data-q');
                refs.chatSubmit.click();
    });
});
        refs.chatInput.addEventListener('keyup', function(e) { if (e.key === 'Enter') refs.chatSubmit.click(); });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
