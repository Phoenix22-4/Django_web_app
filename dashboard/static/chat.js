// AquaSavvy AI Chat Widget - Professional Floating Chat
(function() {
    'use strict';

    // DOM Elements
    const chatFab = document.getElementById('chat-fab');
    const chatPanel = document.getElementById('chat-panel');
    const chatClose = document.getElementById('chat-close');
    const chatMinimize = document.getElementById('chat-minimize');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');

    if (!chatFab || !chatPanel) return;

    // ==================== DRAGGABLE FAB ====================
    let isDragging = false;
    let startY = 0;
    let startBottom = 20;

    chatFab.addEventListener('mousedown', startDrag);
    chatFab.addEventListener('touchstart', startDrag, { passive: false });

    function startDrag(e) {
        if (e.type === 'mousedown' && e.button !== 0) return;
        
        isDragging = true;
        chatFab.classList.add('dragging');
        
        const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;
        startY = clientY;
        
        const computedStyle = window.getComputedStyle(chatFab);
        startBottom = parseInt(computedStyle.bottom);
        
        e.preventDefault();
        
        document.addEventListener('mousemove', doDrag);
        document.addEventListener('touchmove', doDrag, { passive: false });
        document.addEventListener('mouseup', stopDrag);
        document.addEventListener('touchend', stopDrag);
    }

    function doDrag(e) {
        if (!isDragging) return;
        e.preventDefault();
        
        const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;
        const deltaY = startY - clientY; // Inverted for bottom positioning
        let newBottom = startBottom + deltaY;
        
        // Constrain within viewport
        const maxBottom = window.innerHeight - chatFab.offsetHeight - 10;
        const minBottom = 10;
        newBottom = Math.max(minBottom, Math.min(maxBottom, newBottom));
        
        chatFab.style.bottom = newBottom + 'px';
        
        // Update label position
        const label = document.querySelector('.chat-fab-label');
        if (label) {
            label.style.bottom = (newBottom + 12) + 'px';
        }
    }

    function stopDrag(e) {
        if (!isDragging) return;
        
        const endY = e.type === 'touchend' ? e.changedTouches[0].clientY : e.clientY;
        const movedDistance = Math.abs(endY - startY);
        
        isDragging = false;
        chatFab.classList.remove('dragging');
        
        document.removeEventListener('mousemove', doDrag);
        document.removeEventListener('touchmove', doDrag);
        document.removeEventListener('mouseup', stopDrag);
        document.removeEventListener('touchend', stopDrag);
        
        // If didn't move much, treat as click
        if (movedDistance < 5) {
            openChat();
        }
    }

    // ==================== CHAT PANEL CONTROL ====================
    function openChat() {
        chatPanel.classList.add('active');
        chatInput.focus();
    }

    function closeChat() {
        chatPanel.classList.remove('active');
    }

    if (chatClose) {
        chatClose.addEventListener('click', closeChat);
    }

    if (chatMinimize) {
        chatMinimize.addEventListener('click', closeChat);
    }

    // ==================== MESSAGE HANDLING ====================
    function appendMessage(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        // Format text with line breaks and basic HTML support
        const formattedText = text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        content.innerHTML = formattedText;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom with smooth animation
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    function showTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.style.display = 'flex';
        }
    }

    function hideTypingIndicator() {
        if (typingIndicator) {
            typingIndicator.style.display = 'none';
        }
    }

    function getCsrfToken() {
        if (csrfEl && csrfEl.value) return csrfEl.value;
        
        // Fallback to cookie
        const name = 'csrftoken=';
        const decoded = decodeURIComponent(document.cookie);
        const parts = decoded.split(';');
        for (let p of parts) {
            const part = p.trim();
            if (part.startsWith(name)) {
                return part.substring(name.length);
            }
        }
        return '';
    }

    async function sendMessage(message) {
        if (!message.trim()) return;
        
        // Add user message
        appendMessage('user', message);
        chatInput.value = '';
        chatSend.disabled = true;
        showTypingIndicator();
        
        try {
            const response = await fetch('/api/ai_chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            hideTypingIndicator();
            
            const reply = data.reply || 'Sorry, I couldn\'t generate a response. Please try again.';
            appendMessage('bot', reply);
            
        } catch (error) {
            console.error('Chat error:', error);
            hideTypingIndicator();
            appendMessage('bot', '⚠️ Network error. Please check your connection and try again. For urgent assistance, contact: **contact:vision072025@gmail.com** or WhatsApp: **+254 702 715070**');
        } finally {
            chatSend.disabled = false;
            chatInput.focus();
        }
    }

    // ==================== FORM SUBMISSION ====================
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (message) {
                sendMessage(message);
            }
        });
    }

    // ==================== KEYBOARD SHORTCUTS ====================
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            // Submit on Enter (but not Shift+Enter)
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    // ==================== ESCAPE KEY TO CLOSE ====================
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatPanel.classList.contains('active')) {
            closeChat();
        }
    });

    // ==================== CLICK OUTSIDE TO CLOSE ====================
    document.addEventListener('click', function(e) {
        if (chatPanel.classList.contains('active') && 
            !chatPanel.contains(e.target) && 
            !chatFab.contains(e.target)) {
            closeChat();
        }
    });

})();
