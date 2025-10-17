// AquaSavvy AI Chat System
class AquaSavvyChat {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createChatWidget();
        this.setupEventListeners();
    }

    createChatWidget() {
        // Create chat button
        const chatButton = document.createElement('div');
        chatButton.className = 'aquasavvy-chat-button';
        chatButton.innerHTML = `
            <img src="{% static 'images/chat-icon.png' %}" alt="AquaSavvy AI Chat" onerror="this.style.display='none'">
            <span>💬</span>
        `;

        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.className = 'aquasavvy-chat-window';
        chatWindow.innerHTML = `
            <div class="chat-header">
                <h3>AquaSavvy AI Assistant</h3>
                <button class="close-chat">×</button>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="welcome-message">
                    <p>Hi! I'm your AquaSavvy AI assistant. I can help you with:</p>
                    <ul>
                        <li>Water system monitoring and control</li>
                        <li>Device troubleshooting</li>
                        <li>Automation setup</li>
                        <li>System maintenance tips</li>
                    </ul>
                    <p>How can I help you today?</p>
                </div>
            </div>
            <div class="chat-input-area">
                <input type="text" placeholder="Ask me about your water system..." id="chat-input">
                <button id="send-message">
                    <img src="{% static 'images/send-icon.png' %}" alt="Send" onerror="this.style.display='none'">
                    <span>Send</span>
                </button>
            </div>
        `;

        document.body.appendChild(chatButton);
        document.body.appendChild(chatWindow);
    }

    setupEventListeners() {
        // Chat button click
        document.querySelector('.aquasavvy-chat-button').addEventListener('click', () => {
            this.toggleChat();
        });

        // Close chat
        document.querySelector('.close-chat').addEventListener('click', () => {
            this.closeChat();
        });

        // Send message
        document.getElementById('send-message').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter key to send
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const chatWindow = document.querySelector('.aquasavvy-chat-window');
        const chatButton = document.querySelector('.aquasavvy-chat-button');
        
        if (this.isOpen) {
            chatWindow.classList.add('open');
            chatButton.classList.add('active');
            document.getElementById('chat-input').focus();
        } else {
            chatWindow.classList.remove('open');
            chatButton.classList.remove('active');
        }
    }

    closeChat() {
        this.isOpen = false;
        document.querySelector('.aquasavvy-chat-window').classList.remove('open');
        document.querySelector('.aquasavvy-chat-button').classList.remove('active');
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message
        this.addMessage('user', message);
        input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to backend
            const response = await fetch('/api/ai_chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            if (data.reply) {
                this.addMessage('assistant', data.reply);
            } else {
                this.addMessage('error', 'Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('error', 'Connection error. Please check your internet connection.');
        }
    }

    addMessage(type, content) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        if (type === 'user') {
            messageDiv.innerHTML = `<p>${content}</p>`;
        } else if (type === 'assistant') {
            messageDiv.innerHTML = `<p>${content}</p>`;
        } else if (type === 'error') {
            messageDiv.innerHTML = `<p style="color: #dc3545;">${content}</p>`;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '<p>AquaSavvy AI is typing...</p>';
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new AquaSavvyChat();
});
