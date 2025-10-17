// dashboard/static/chat.js
// Controls the floating AI chat widget (Amazon/Redmi style)

document.addEventListener('DOMContentLoaded', function() {
    const chatIcon = document.getElementById('ai-chat-icon');
    const chatPanel = document.getElementById('ai-chat-panel');
    const chatClose = document.getElementById('ai-chat-close');
    const chatSend = document.getElementById('ai-chat-send');
    const chatInput = document.getElementById('ai-chat-input');
    const messageDisplay = document.getElementById('ai-chat-messages');
    
    // Ensure essential elements exist
    if (!chatIcon || !chatPanel || !chatClose || !chatSend || !chatInput || !messageDisplay) {
        console.error("AquaSavvy Chat: One or more essential chat elements are missing from the page.");
        return; 
    }
    
    // Attempt to get CSRF token (might be null if {% csrf_token %} is missing)
    const csrfTokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';
    if (!csrfToken) {
        console.warn("AquaSavvy Chat: CSRF token not found. POST requests might fail.");
    }

    // --- Event Listeners ---

    // Open chat panel
    chatIcon.addEventListener('click', () => {
        chatPanel.classList.add('visible');
        chatIcon.classList.add('hidden');
        chatInput.focus(); // Focus input when opened
    });

    // Close chat panel
    chatClose.addEventListener('click', () => {
        chatPanel.classList.remove('visible');
        chatIcon.classList.remove('hidden');
    });

    // Send message on button click
    chatSend.addEventListener('click', sendMessage);
    
    // Send message on Enter key press in input
    chatInput.addEventListener('keypress', function(e) {
        // Check if Enter key was pressed (and Shift key was not, to allow multi-line input if needed later)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // Prevent default form submission/newline
            sendMessage();
        }
    });

    // --- Core Functions ---

    async function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText === "") return; // Don't send empty messages

        // Add user message visually
        addMessage(messageText, 'user-message');
        chatInput.value = ''; // Clear input field
        
        // Indicate loading state
        setLoadingState(true);
        
        // Determine the correct API endpoint based on the current page
        // Assumes public homepage is '/home/' or '/'
        const isPublicPage = ['/home/', '/'].includes(window.location.pathname);
        const chatApiUrl = isPublicPage ? '/api/ai_chat_public/' : '/api/ai_chat/';

        try {
            const response = await fetch(chatApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Send CSRF token for security
                },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) { 
                // Handle HTTP errors (like 403 Forbidden, 500 Internal Server Error)
                throw new Error(`HTTP error ${response.status}`); 
            }

            const data = await response.json();
            
            // Display the response or error from the backend
            if (data.error) {
                addMessage(data.error, 'ai-message error');
            } else {
                addMessage(data.reply || 'Sorry, I received an empty response.', 'ai-message');
            }

        } catch (error) {
            // Handle network errors (e.g., server down, CORS issues) or HTTP errors
            console.error('Error sending chat message:', error);
            // Provide a helpful error message to the user
            addMessage(`⚠️ Network Error: Could not connect. Please check your connection or try again later. (Details: ${error.message})`, 'ai-message error');
        } finally {
            // Reset loading state regardless of success or failure
            setLoadingState(false);
        }
    }

    // Helper to add a message bubble to the chat window
    function addMessage(text, className) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', className);
        // Basic sanitization: display text content only to prevent XSS
        messageElement.textContent = text; 
        messageDisplay.appendChild(messageElement);
        
        // Auto-scroll to the newest message
        messageDisplay.scrollTop = messageDisplay.scrollHeight;
    }

    // Helper to manage the loading state of the send button
    function setLoadingState(isLoading) {
        if (isLoading) {
            chatSend.disabled = true;
            // Simple text indicator, replace with spinner if needed
            chatSend.innerHTML = '...'; 
        } else {
            chatSend.disabled = false;
            // Restore the send icon
            chatSend.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"/></svg>';
            chatInput.focus(); // Re-focus the input field
        }
    }

    // Optional: Close chat panel when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatPanel.classList.contains('visible')) {
            chatPanel.classList.remove('visible');
            chatIcon.classList.remove('hidden');
        }
    });
});
