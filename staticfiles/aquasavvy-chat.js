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
            <img src="/static/images/chat-icon.png" alt="AquaSavvy AI Chat" onerror="this.style.display='none'">
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
                    <p><strong>AquaSavvy AI Assistant</strong></p>
                    <p>I help with water system monitoring, pump control, and troubleshooting.</p>
                    <p>Ask me anything about your system!</p>
                </div>
            </div>
            <div class="chat-input-area">
                <input type="text" placeholder="Ask me about your water system..." id="chat-input">
                <button id="send-message">
                    <img src="/static/images/send-icon.png" alt="Send" onerror="this.style.display='none'">
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
            // Try streaming first
            await this.sendStreamingMessage(message);
        } catch (streamError) {
            // Fallback to regular request
            console.log('Streaming failed, falling back to regular request:', streamError);
            await this.sendRegularMessage(message);
        }
    }

    async sendStreamingMessage(message) {
        const response = await fetch('/api/ai_chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ 
                message: message, 
                stream: true 
            })
        });

        if (!response.ok) {
            throw new Error('Streaming request failed');
        }

        // Remove typing indicator
        this.hideTypingIndicator();

        // Create assistant message container
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant streaming';
        messageDiv.innerHTML = '<p></p>';
        messagesContainer.appendChild(messageDiv);
        
        const messageText = messageDiv.querySelector('p');
        let fullResponse = '';

        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            messageDiv.classList.remove('streaming');
                            return;
                        }

                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.chunk) {
                                fullResponse += parsed.chunk;
                                messageText.textContent = fullResponse;
                                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                            } else if (parsed.reply) {
                                messageText.textContent = parsed.reply;
                                messageDiv.classList.remove('streaming');
                                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                                return;
                            }
                        } catch (e) {
                            // Ignore parsing errors for incomplete chunks
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }

    async sendRegularMessage(message) {
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
