// dashboard/static/chat.js
// Floating chat widget: binds to widget HTML in base.html; posts to Django Gemini endpoints

(function() {
    function qs(sel) { return document.querySelector(sel); }
    function qsa(sel) { return Array.from(document.querySelectorAll(sel)); }

    // No HTML/CSS injection here; base.html provides the widget markup and dashboard.css provides styles

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
        bindEvents();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
