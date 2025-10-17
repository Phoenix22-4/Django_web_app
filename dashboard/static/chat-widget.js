// Based on the example by Anant Parmar, adapted for AquaSavvy & Gemini API
(function() {
    // 1. INJECT STYLES (Tailwind + Custom)
    if (!document.querySelector('link[href*="tailwindcss"]')) {
        document.head.insertAdjacentHTML('beforeend', '<link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.16/tailwind.min.css" rel="stylesheet">');
    }

    const style = document.createElement('style');
    style.innerHTML = `
    .hidden {
        display: none;
    }
    #chat-widget-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        flex-direction: column;
    }
    #chat-popup {
        height: 70vh;
        max-height: 500px;
        width: 350px;
        transition: all 0.3s;
        overflow: hidden;
        z-index: 9998;
    }
    #chat-bubble {
        z-index: 9999;
        box-shadow: 0 4px 20px rgba(0, 123, 255, 0.4);
    }
    /* Mobile styles from example */
    @media (max-width: 768px) {
        #chat-popup {
            position: fixed;
            top: 0; right: 0; bottom: 0; left: 0;
            width: 100%; height: 100%;
            max-height: 100%;
            border-radius: 0;
        }
    }
    /* Custom message bubble styles for our app */
    .aquasavvy-user-msg {
        background-color: #007bff;
        color: white;
    }
    .aquasavvy-ai-msg {
        background-color: #f1f1f1;
        color: #333;
    }
    .aquasavvy-ai-msg.error {
        background-color: #fff0f0;
        color: #d90000;
    }
    `;
    document.head.appendChild(style);

    // 2. CREATE CHAT WIDGET CONTAINER
    const chatWidgetContainer = document.createElement('div');
    chatWidgetContainer.id = 'chat-widget-container';
    document.body.appendChild(chatWidgetContainer);
    
    // 3. INJECT HTML (Modified for AquaSavvy)
    chatWidgetContainer.innerHTML = `
        <div id="chat-bubble" class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center cursor-pointer text-3xl">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
        </div>
        <div id="chat-popup" class="hidden absolute bottom-20 right-0 w-96 bg-white rounded-md shadow-xl flex flex-col text-sm">
            <div id="chat-header" class="flex justify-between items-center p-4 bg-blue-600 text-white rounded-t-md">
                <h3 class="m-0 text-lg">AquaSavvy AI Assistant</h3>
                <button id="close-popup" class="bg-transparent border-none text-white cursor-pointer">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div id="chat-messages" class="flex-1 p-4 overflow-y-auto">
                <div class="flex mb-3">
                    <div class="aquasavvy-ai-msg rounded-lg py-2 px-4 max-w-[80%]">
                        Hello! I'm the AquaSavvy AI. Ask me about our products or your system.
                    </div>
                </div>
            </div>
            <div id="chat-input-container" class="p-4 border-t border-gray-200">
                <div class="flex space-x-4 items-center">
                    <input type="text" id="chat-input" class="flex-1 border border-gray-300 rounded-md px-4 py-2 outline-none w-3/4" placeholder="Type your message...">
                    <button id="chat-submit" class="bg-blue-600 text-white rounded-md px-4 py-2 cursor-pointer">Send</button>
                </div>
            </div>
        </div>
    `;

    // 4. ADD EVENT LISTENERS & API LOGIC
    const chatInput = document.getElementById('chat-input');
    const chatSubmit = document.getElementById('chat-submit');
    const chatMessages = document.getElementById('chat-messages');
    const chatBubble = document.getElementById('chat-bubble');
    const chatPopup = document.getElementById('chat-popup');
    const closePopup = document.getElementById('close-popup');

    // Get CSRF token (hidden input or cookie); safe fallback for public pages
    function getCookie(name){
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return '';
    }
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrfToken = csrfInput ? csrfInput.value : (getCookie('csrftoken') || '');

    chatSubmit.addEventListener('click', sendMessage);
    chatInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
    chatBubble.addEventListener('click', togglePopup);
    closePopup.addEventListener('click', togglePopup);

    function togglePopup() {
        chatPopup.classList.toggle('hidden');
        if (!chatPopup.classList.contains('hidden')) {
            chatInput.focus();
        }
    }  

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        displayUserMessage(message);
        chatInput.value = '';

        // Determine which API to call
        const path = window.location.pathname || '/';
        const isPublicPage = (path === '/' || path.startsWith('/home/'));
        const chatApiUrl = isPublicPage ? '/api/ai_chat_public/' : '/api/ai_chat/';

        try {
            const headers = { 'Content-Type': 'application/json' };
            if (csrfToken) headers['X-CSRFToken'] = csrfToken;
            const response = await fetch(chatApiUrl, {
                method: 'POST',
                headers,
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                displayAiMessage(data.error, true);
            } else {
                displayAiMessage(data.reply);
            }

        } catch (error) {
            console.error('Error fetching AI response:', error);
            displayAiMessage('Network Error. Please check your connection and try again.', true);
        }
    }

    function displayUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'flex justify-end mb-3';
        messageElement.innerHTML = `
            <div class="aquasavvy-user-msg rounded-lg py-2 px-4 max-w-[80%]">
                ${message}
            </div>
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  
    function displayAiMessage(message, isError = false) {
        const replyElement = document.createElement('div');
        replyElement.className = 'flex mb-3';
        let errorClass = isError ? ' error' : '';
        replyElement.innerHTML = `
            <div class="aquasavvy-ai-msg${errorClass} rounded-lg py-2 px-4 max-w-[80%]">
                ${message}
            </div>
        `;
        chatMessages.appendChild(replyElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
})();
