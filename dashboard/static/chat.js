// dashboard/static/chat.js
// AquaSavvy AI Chat Widget - Smart routing for public/private endpoints
document.addEventListener('DOMContentLoaded', function() {
    const chatIcon = document.getElementById('ai-chat-icon');
    const chatPanel = document.getElementById('ai-chat-panel');
    const chatClose = document.getElementById('ai-chat-close');
    const chatSend = document.getElementById('ai-chat-send');
    const chatInput = document.getElementById('ai-chat-input');
    const messageDisplay = document.getElementById('ai-chat-messages');
    
    if (!chatIcon || !chatPanel) return;
    
    // Get the CSRF token from the <input> tag in base.html
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    // Open chat panel
    chatIcon.addEventListener('click', () => {
        chatPanel.classList.add('visible');
        chatIcon.classList.add('hidden');
        chatInput.focus();
    });

    // Close chat panel
    chatClose.addEventListener('click', () => {
        chatPanel.classList.remove('visible');
        chatIcon.classList.remove('hidden');
    });

    // Send message on button click
    chatSend.addEventListener('click', sendMessage);
    
    // Send message on Enter key
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    async function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText === "") return;

        // Add user message to chat
        addMessage(messageText, 'user-message');
        chatInput.value = '';
        
        // Disable send button while processing
        chatSend.disabled = true;
        chatSend.textContent = '...';
        
        // Determine which chat API to call (public or private)
        const isPublicPage = window.location.pathname === '/home/' || window.location.pathname === '/';
        const chatApiUrl = isPublicPage ? '/api/ai_chat_public/' : '/api/ai_chat/';

        try {
            const response = await fetch(chatApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken 
                },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) { 
                throw new Error(`HTTP ${response.status}`); 
            }

            const data = await response.json();
            
            if (data.error) {
                addMessage(data.error, 'ai-message error');
            } else {
                addMessage(data.reply || 'No response received.', 'ai-message');
            }

        } catch (error) {
            console.error('Error sending chat message:', error);
            addMessage("⚠️ Network Error: Could not connect to the AI assistant. For support, contact: contact:vision072025@gmail.com or WhatsApp: +254 702 715070", 'ai-message error');
        } finally {
            // Re-enable send button
            chatSend.disabled = false;
            chatSend.textContent = 'Send';
            chatInput.focus();
        }
    }

    function addMessage(text, className) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', className);
        messageElement.textContent = text;
        messageDisplay.appendChild(messageElement);
        
        // Auto-scroll to bottom
        messageDisplay.scrollTop = messageDisplay.scrollHeight;
    }

    // Close chat when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatPanel.classList.contains('visible')) {
            chatPanel.classList.remove('visible');
            chatIcon.classList.remove('hidden');
        }
    });
});
