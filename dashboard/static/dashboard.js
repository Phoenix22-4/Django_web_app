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
        tanksContainer: document.querySelector('.tanks-container')
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

            // Handle dynamic tanks if available
            if (data.tanks && Array.isArray(data.tanks)) {
                updateDynamicTanks(data.tanks);
            } else {
                // Fallback to old overhead/underground system
                safeStyleUpdate(elements.overheadWater, 'height', `${data.overhead_level || 0}%`);
                safeUpdate(elements.overheadLevelText, `${data.overhead_level || 0}%`);
                safeStyleUpdate(elements.undergroundWater, 'height', `${data.underground_level || 0}%`);
                safeUpdate(elements.undergroundLevelText, `${data.underground_level || 0}%`);
                updateStatusMessages(data.overhead_level || 0, data.underground_level || 0);
            }

            const pumpIsOn = data.pump_status;
            safeUpdate(elements.pumpStatusText, pumpIsOn ? "ON" : "OFF");
            
            // --- THIS IS THE KEY FOR THE ANIMATION ---
            // This line adds the 'active' class when the pump is on.
            safeClassToggle(elements.pumpMotor, 'active', pumpIsOn);
            
            safeClassToggle(elements.pumpMotor, 'online', pumpIsOn);
            safeClassToggle(elements.pumpMotor, 'offline', !pumpIsOn);

            safeUpdate(elements.pumpCurrentText, `${data.pump_current?.toFixed(1) || '0.0'} A`);

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

    // Dynamic tank update function
    function updateDynamicTanks(tanks) {
        if (!elements.tanksContainer) return;
        
        // Keep track of which tanks we've seen
        let seenTankSlugs = [];

        tanks.forEach(tank => {
            const tankSlug = slugify(tank.name);
            seenTankSlugs.push(tankSlug);
            
            let tankWrapper = document.getElementById(`tank-wrapper-${tankSlug}`);
            
            // If tank HTML doesn't exist, create it
            if (!tankWrapper) {
                tankWrapper = document.createElement('div');
                tankWrapper.className = 'tank-wrapper';
                tankWrapper.id = `tank-wrapper-${tankSlug}`;
                
                const tankTypeClass = tank.name.toLowerCase().includes('underground') ? 'underground' : 'overhead';
                
                tankWrapper.innerHTML = `
                    <div class="tank-title">${tank.name}</div>
                    <div class="tank ${tankTypeClass}">
                        <div class="tank-frame">
                            <div class="water-level" id="tank-level-${tankSlug}"></div>
                        </div>
                        <div class="tank-info"><span id="tank-percent-${tankSlug}">--%</span></div>
                    </div>
                `;
                elements.tanksContainer.appendChild(tankWrapper);
            }
            
            // Update the levels
            const levelElement = document.getElementById(`tank-level-${tankSlug}`);
            const percentElement = document.getElementById(`tank-percent-${tankSlug}`);
            
            safeStyleUpdate(levelElement, 'height', `${tank.level}%`);
            safeUpdate(percentElement, `${tank.level}%`);
        });

        // Remove any old tanks that are no longer in the data
        elements.tanksContainer.querySelectorAll('.tank-wrapper').forEach(wrapper => {
            const slug = wrapper.id.replace('tank-wrapper-', '');
            if (!seenTankSlugs.includes(slug)) {
                wrapper.remove();
            }
        });

        // Update status messages for dynamic tanks
        updateDynamicStatusMessages(tanks);
    }

    function updateDynamicStatusMessages(tanks) {
        // Clear existing status messages
        const statusContainer = document.getElementById('status-messages-box');
        if (statusContainer) {
            statusContainer.innerHTML = '';
            
            tanks.forEach(tank => {
                let p = document.createElement('p');
                p.id = `status-msg-${slugify(tank.name)}`;
                
                if (tank.level < 10) {
                    p.textContent = `${tank.name}: CRITICAL!`;
                    p.style.color = "red";
                } else if (tank.level < 25) {
                    p.textContent = `${tank.name}: Low`;
                    p.style.color = "orange";
                } else if (tank.level > 95) {
                    p.textContent = `${tank.name}: FULL`;
                    p.style.color = "blue";
                } else {
                    p.textContent = `${tank.name}: ${tank.level}%`;
                    p.style.color = "";
                }
                statusContainer.appendChild(p);
            });
        }
    }

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

    function slugify(text) {
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')       // Replace spaces with -
            .replace(/[^\w\-]+/g, '')   // Remove all non-word chars
            .replace(/\-\-+/g, '-')     // Replace multiple - with single -
            .replace(/^-+/, '')        // Trim - from start of text
            .replace(/-+$/, '');       // Trim - from end of text
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
});