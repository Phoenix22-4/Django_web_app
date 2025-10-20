// Chat Widget JavaScript
// This file handles the AquaSavvy AI chat widget functionality

console.log('Chat widget script loaded');

// Initialize chat widget when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Chat widget initialized');
    
    // Create chat widget if it doesn't exist
    if (!document.getElementById('aquasavvy-chat-widget')) {
        createChatWidget();
    }
});

function createChatWidget() {
    // Create the chat widget container
    const chatWidget = document.createElement('div');
    chatWidget.id = 'aquasavvy-chat-widget';
    chatWidget.innerHTML = `
        <div class="chat-widget-container">
            <div class="chat-header">
                <h3>AquaSavvy AI Assistant</h3>
                <button id="chat-close-btn" class="chat-close-btn">&times;</button>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="chat-message bot-message">
                    <p>Hello! I'm AquaSavvy, your water management AI assistant. How can I help you today?</p>
                </div>
            </div>
            <div class="chat-input-container">
                <input type="text" id="chat-input" placeholder="Type your message..." />
                <button id="chat-send-btn" class="chat-send-btn">Send</button>
            </div>
        </div>
        <button id="chat-toggle-btn" class="chat-toggle-btn">
            <i class="fas fa-comments"></i>
        </button>
    `;
    
    // Add to page
    document.body.appendChild(chatWidget);
    
    // Add event listeners
    setupChatEventListeners();
}

function setupChatEventListeners() {
    const toggleBtn = document.getElementById('chat-toggle-btn');
    const closeBtn = document.getElementById('chat-close-btn');
    const sendBtn = document.getElementById('chat-send-btn');
    const input = document.getElementById('chat-input');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleChat);
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeChat);
    }
    
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

function toggleChat() {
    const widget = document.getElementById('aquasavvy-chat-widget');
    if (widget) {
        widget.classList.toggle('chat-open');
    }
}

function closeChat() {
    const widget = document.getElementById('aquasavvy-chat-widget');
    if (widget) {
        widget.classList.remove('chat-open');
    }
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');
    
    if (input && messages && input.value.trim()) {
        const message = input.value.trim();
        
        // Add user message
        addMessage(message, 'user');
        
        // Clear input
        input.value = '';
        
        // Simulate AI response
        setTimeout(() => {
            addMessage('Thank you for your message! I\'m here to help with your water management needs.', 'bot');
        }, 1000);
    }
}

function addMessage(text, sender) {
    const messages = document.getElementById('chat-messages');
    if (messages) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        messageDiv.innerHTML = `<p>${text}</p>`;
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }
}