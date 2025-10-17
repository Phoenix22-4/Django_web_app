// dashboard/static/chat.js
// Injects floating chat widget (per provided snippet) and wires to Django Gemini endpoints

(function() {
    function qs(sel) { return document.querySelector(sel); }
    function qsa(sel) { return Array.from(document.querySelectorAll(sel)); }

    // Inject Tailwind link and minimal inline styles like the provided snippet
    function ensureTailwindAndStyles() {
        document.head.insertAdjacentHTML('beforeend', '<link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.16/tailwind.min.css" rel="stylesheet">');
        const style = document.createElement('style');
        style.innerHTML = `
        .hidden { display: none; }
        #chat-widget-container { position: fixed; bottom: 20px; right: 20px; flex-direction: column; }
        #chat-popup { height: 70vh; max-height: 70vh; transition: all 0.3s; overflow: hidden; }
        @media (max-width: 768px) {
            #chat-popup { position: fixed; top: 0; right: 0; bottom: 0; left: 0; width: 100%; height: 100%; max-height: 100%; border-radius: 0; }
        }`;
        document.head.appendChild(style);
    }

    function injectWidgetHtmlIfMissing() {
        if (qs('#chat-widget-container')) return;
        const chatWidgetContainer = document.createElement('div');
        chatWidgetContainer.id = 'chat-widget-container';
        document.body.appendChild(chatWidgetContainer);
        chatWidgetContainer.innerHTML = `
        <div id="chat-bubble" class="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center cursor-pointer text-3xl">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <div id="chat-popup" class="hidden absolute bottom-20 right-0 w-96 bg-white rounded-md shadow-md flex flex-col transition-all text-sm">
          <div id="chat-header" class="flex justify-between items-center p-4 bg-gray-800 text-white rounded-t-md">
            <h3 class="m-0 text-lg">AquaSavvy AI Assistant (Gemini)</h3>
            <button id="close-popup" class="bg-transparent border-none text-white cursor-pointer">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div id="chat-messages" class="flex-1 p-4 overflow-y-auto"></div>
          <div id="chat-input-container" class="p-4 border-t border-gray-200">
            <div class="flex space-x-4 items-center">
              <input type="text" id="chat-input" class="flex-1 border border-gray-300 rounded-md px-4 py-2 outline-none w-3/4" placeholder="Ask about AquaSavvy...">
              <button id="chat-submit" class="bg-gray-800 text-white rounded-md px-4 py-2 cursor-pointer">Send</button>
            </div>
            <div class="flex text-center text-xs pt-4"><span class="flex-1">Powered by Gemini</span></div>
          </div>
        </div>`;
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return '';
    }

    function getCsrfToken() {
        const input = document.querySelector('#chat-input-container input[name="csrfmiddlewaretoken"]');
        if (input) return input.value;
        return getCookie('csrftoken') || '';
    }

    function isPublicPage() {
        const path = window.location.pathname || '/';
        return path === '/' || path.startsWith('/home/');
    }

    function endpointForPage() {
        return isPublicPage() ? '/api/ai_chat_public/' : '/api/ai_chat/';
    }

    function reply(message) {
        const chatMessages = qs('#chat-messages');
        const el = document.createElement('div');
        el.className = 'flex mb-3';
        el.innerHTML = `<div class="bg-gray-200 text-black rounded-lg py-2 px-4 max-w-[70%]">${escapeHtml(message)}</div>`;
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendUser(message) {
        const chatMessages = qs('#chat-messages');
        const el = document.createElement('div');
        el.className = 'flex justify-end mb-3';
        el.innerHTML = `<div class="bg-gray-800 text-white rounded-lg py-2 px-4 max-w-[70%]">${escapeHtml(message)}</div>`;
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function onUserRequest(message) {
        appendUser(message);
        const url = endpointForPage();
        const csrf = getCsrfToken();
        try {
            const resp = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf
                },
                body: JSON.stringify({ message })
            });
            const data = await resp.json().catch(() => ({}));
            const text = (data && (data.reply || data.error)) || (resp.ok ? 'No response.' : 'Server error.');
            reply(text);
        } catch (e) {
            reply(`Network error: ${e && e.message ? e.message : e}`);
        }
    }

    function togglePopup() {
        const chatPopup = qs('#chat-popup');
        chatPopup.classList.toggle('hidden');
        if (!chatPopup.classList.contains('hidden')) {
            const input = qs('#chat-input');
            if (input) input.focus();
        }
    }

    function bindEvents() {
        const chatInput = qs('#chat-input');
        const chatSubmit = qs('#chat-submit');
        const chatBubble = qs('#chat-bubble');
        const closePopup = qs('#close-popup');

        if (chatSubmit) {
            chatSubmit.addEventListener('click', function() {
                const message = (chatInput && chatInput.value || '').trim();
                if (!message) return;
                if (chatInput) chatInput.value = '';
                onUserRequest(message);
            });
        }
        if (chatInput) {
            chatInput.addEventListener('keyup', function(event) {
                if (event.key === 'Enter') {
                    chatSubmit && chatSubmit.click();
                }
            });
        }
        if (chatBubble) chatBubble.addEventListener('click', togglePopup);
        if (closePopup) closePopup.addEventListener('click', togglePopup);
    }

    function init() {
        ensureTailwindAndStyles();
        injectWidgetHtmlIfMissing();
        bindEvents();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
