// dashboard/static/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");

    const deviceIdElement = document.getElementById('device-id');
    if (!deviceIdElement) {
        console.error("ERROR: Device ID meta tag not found!");
        return;
    }
    const deviceId = deviceIdElement.getAttribute('content');
    console.log(`Device ID: ${deviceId}`);

    const socketProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socketURL = `${socketProtocol}//${window.location.host}/ws/dashboard/${deviceId}/`;
    console.log(`Connecting to WebSocket: ${socketURL}`);
    const socket = new WebSocket(socketURL);

    const elements = {
        websocketStatus: document.getElementById('websocket-status'),
        websocketLight: document.getElementById('websocket-light'),
        deviceStatus: document.getElementById('device-status'),
        deviceLight: document.getElementById('device-light'),
        overheadWater: document.getElementById('overhead-water'),
        overheadLevelText: document.getElementById('overhead-level'),
        undergroundWater: document.getElementById('underground-water'),
        undergroundLevelText: document.getElementById('underground-level'),
        pumpStatusText: document.getElementById('pump-status-text'),
        pumpCurrentText: document.getElementById('pump-current-text'),
        pumpMotor: document.getElementById('pump-motor'),
        pumpOnBtn: document.getElementById('pump-on'),
        pumpOffBtn: document.getElementById('pump-off'),
        overheadStatusMsg: document.getElementById('overhead-status-msg'),
        undergroundStatusMsg: document.getElementById('underground-status-msg'),
        chatLauncher: document.getElementById('chat-launcher'),
        chatPanel: document.getElementById('chat-panel'),
        chatClose: document.getElementById('chat-close'),
        chatMessages: document.getElementById('chat-messages'),
        chatForm: document.getElementById('chat-form'),
        chatInput: document.getElementById('chat-input')
    };

    Object.entries(elements).forEach(([key, element]) => {
        if (!element) console.error(`Missing element: ${key}`);
    });

    socket.onopen = function(e) {
        console.log("WebSocket connection established");
        updateConnectionStatus('websocket', 'Online', 'online');
        updateConnectionStatus('device', 'Connecting...', 'connecting');
    };

    socket.onmessage = function(e) {
        console.log("WebSocket message received");
        try {
            const data = JSON.parse(e.data);
            console.log("Parsed data:", data);

            updateConnectionStatus('device', 'Online', 'online');

            safeStyleUpdate(elements.overheadWater, 'height', `${data.overhead_level}%`);
            safeUpdate(elements.overheadLevelText, `${data.overhead_level}%`);
            safeStyleUpdate(elements.undergroundWater, 'height', `${data.underground_level}%`);
            safeUpdate(elements.undergroundLevelText, `${data.underground_level}%`);

            const pumpIsOn = data.pump_status;
            safeUpdate(elements.pumpStatusText, pumpIsOn ? "ON" : "OFF");
            
            // --- THIS IS THE KEY FOR THE ANIMATION ---
            // This line adds the 'active' class when the pump is on.
            safeClassToggle(elements.pumpMotor, 'active', pumpIsOn);
            
            safeClassToggle(elements.pumpMotor, 'online', pumpIsOn);
            safeClassToggle(elements.pumpMotor, 'offline', !pumpIsOn);

            // Toggle pump LED indicator
            const pumpLedEl = document.getElementById('pump-led');
            if (pumpLedEl) {
                if (pumpIsOn === true) {
                    pumpLedEl.classList.add('led-on');
                    pumpLedEl.classList.remove('led-off');
                } else {
                    pumpLedEl.classList.add('led-off');
                    pumpLedEl.classList.remove('led-on');
                }
            }

            safeUpdate(elements.pumpCurrentText, `${data.pump_current?.toFixed(1) || '0.0'} A`);
            updateStatusMessages(data.overhead_level, data.underground_level);

        } catch (error) {
            console.error("Error processing message:", error);
            updateConnectionStatus('device', 'Error', 'error');
        }
    };

    socket.onclose = function(e) {
        console.log("WebSocket connection closed");
        updateConnectionStatus('websocket', 'Offline', 'offline');
        updateConnectionStatus('device', 'Disconnected', 'offline');
    };

    socket.onerror = function(error) {
        console.error("WebSocket error:", error);
        updateConnectionStatus('websocket', 'Error', 'error');
    };

    function safeUpdate(element, value) {
        if (element) element.textContent = value;
    }

    function safeStyleUpdate(element, style, value) {
        if (element) element.style[style] = value;
    }

    function safeClassUpdate(element, className) {
        if (element) element.className = className;
    }

    function safeClassToggle(element, className, state) {
        if (element) element.classList.toggle(className, state);
    }

    function updateConnectionStatus(type, text, state) {
        const statusElement = type === 'websocket' ? elements.websocketStatus : elements.deviceStatus;
        const lightElement = type === 'websocket' ? elements.websocketLight : elements.deviceLight;
        
        safeUpdate(statusElement, text);
        safeClassUpdate(lightElement, `status-light ${state}`);
    }

    function updateStatusMessages(overhead, underground) {
        if (elements.overheadStatusMsg) {
            if (overhead >= 95) {
                elements.overheadStatusMsg.textContent = "Overhead Tank: FULL";
                elements.overheadStatusMsg.style.color = "blue";
            } else {
                elements.overheadStatusMsg.textContent = `Overhead Tank: ${overhead}%`;
                elements.overheadStatusMsg.style.color = "";
            }
        }

        if (elements.undergroundStatusMsg) {
            if (underground < 10) {
                elements.undergroundStatusMsg.textContent = "Underground: CRITICAL!";
                elements.undergroundStatusMsg.style.color = "red";
            } else if (underground < 25) {
                elements.undergroundStatusMsg.textContent = "Underground: Low";
                elements.undergroundStatusMsg.style.color = "orange";
            } else {
                elements.undergroundStatusMsg.textContent = `Underground Tank: ${underground}%`;
                elements.undergroundStatusMsg.style.color = "";
            }
        }
    }

    if (elements.pumpOnBtn) {
        elements.pumpOnBtn.addEventListener('click', () => {
            socket.send(JSON.stringify({command: 'PUMP_ON'}));
            console.log("PUMP_ON command sent");
        });
    }

    if (elements.pumpOffBtn) {
        elements.pumpOffBtn.addEventListener('click', () => {
            socket.send(JSON.stringify({command: 'PUMP_OFF'}));
            console.log("PUMP_OFF command sent");
        });
    }

    // ==================== CHAT WIDGET LOGIC ====================
    if (elements.chatLauncher && elements.chatPanel && elements.chatClose) {
        elements.chatLauncher.addEventListener('click', () => {
            elements.chatPanel.style.display = 'flex';
        });
        elements.chatClose.addEventListener('click', () => {
            elements.chatPanel.style.display = 'none';
        });
    }

    function appendChatMessage(role, text) {
        if (!elements.chatMessages) return;
        const div = document.createElement('div');
        div.className = `chat-msg ${role}`;
        div.textContent = text;
        elements.chatMessages.appendChild(div);
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }

    function getCsrfToken() {
        const name = 'csrftoken=';
        const decoded = decodeURIComponent(document.cookie);
        const parts = decoded.split(';');
        for (let p of parts) {
            const part = p.trim();
            if (part.startsWith(name)) return part.substring(name.length);
        }
        return '';
    }

    if (elements.chatForm && elements.chatInput) {
        elements.chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = elements.chatInput.value.trim();
            if (!msg) return;
            appendChatMessage('user', msg);
            elements.chatInput.value = '';
            try {
                const resp = await fetch('/api/ai_chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ message: msg })
                });
                const data = await resp.json();
                appendChatMessage('bot', data.reply || 'No response');
            } catch (err) {
                appendChatMessage('bot', 'Network error. Please try again later.');
            }
        });
    }
});