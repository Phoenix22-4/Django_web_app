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
        pumpStatusText: document.getElementById('pump-status-text'),
        pumpCurrentText: document.getElementById('pump-current-text'),
        pumpMotor: document.getElementById('pump-motor'),
        pumpOnBtn: document.getElementById('pump-on-btn'),
        pumpOffBtn: document.getElementById('pump-off-btn'),
        tanksContainer: document.querySelector('.tank-system-container'),
        statusMessagesContainer: document.getElementById('status-message')
    };

    Object.entries(elements).forEach(([key, element]) => {
        if (!element) console.error(`Missing element: ${key}`);
    });

    socket.onopen = function(e) {
        console.log("WebSocket connection established");
        updateConnectionStatus('websocket', 'Online', 'online');
        updateConnectionStatus('device', 'Connecting...', 'connecting');
        
        // Load device data to get tank names
        loadDeviceData();
    };

    socket.onmessage = function(e) {
        console.log("WebSocket message received");
        try {
            const data = JSON.parse(e.data);
            console.log("Parsed data:", data);

            updateConnectionStatus('device', 'Online', 'online');

            // Update status message with WebSocket data
            updateStatusMessage(data);

            // Handle dynamic system data
            updateDynamicSystemData(data);

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

    // Load device data to get tank names
    function loadDeviceData() {
        fetch(`/api/device_data/${deviceId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Device data loaded:', data.device);
                    // Store device data globally for tank name mapping
                    window.deviceData = data.device;
                }
            })
            .catch(error => {
                console.error('Error loading device data:', error);
            });
    }

    // Dynamic system data update function
    function updateDynamicSystemData(data) {
        if (!elements.tanksContainer) return;
        
        // Extract level data and create tanks
        const levelData = [];
        for (const [key, value] of Object.entries(data)) {
            if (key.endsWith('_level')) {
                levelData.push({
                    reading_id: key,
                    level: value,
                    name: getTankNameFromReadingId(key)
                });
            }
        }
        
        // Update tanks with level data
        updateDynamicTanks(levelData);
        
        // Update pump status
        if (data.pump_status !== undefined) {
            const pumpIsOn = data.pump_status;
            safeUpdate(elements.pumpStatusText, pumpIsOn ? "ON" : "OFF");
            safeClassToggle(elements.pumpMotor, 'active', pumpIsOn);
            safeClassToggle(elements.pumpMotor, 'online', pumpIsOn);
            safeClassToggle(elements.pumpMotor, 'offline', !pumpIsOn);
        }
        
        // Update pump current
        if (data.pump_current !== undefined) {
            safeUpdate(elements.pumpCurrentText, `${data.pump_current.toFixed(1)} A`);
        }
        
        // Update status messages
        updateStatusMessages(data);
    }
    
    // Get tank name from reading ID using device data
    function getTankNameFromReadingId(readingId) {
        if (!window.deviceData) return readingId;
        
        // Check which tank slot has this reading ID
        for (let i = 1; i <= 4; i++) {
            const readingIdField = `tank_${i}_reading_id`;
            const nameField = `tank_${i}_name`;
            
            if (window.deviceData[readingIdField] === readingId) {
                return window.deviceData[nameField] || readingId;
            }
        }
        
        return readingId;
    }

    // Dynamic tank update function
    function updateDynamicTanks(tanks) {
        if (!elements.tanksContainer) return;
        
        // Keep track of which tanks we've seen
        let seenTankSlugs = [];

        tanks.forEach((tank, index) => {
            // Use device tank names if available, otherwise use tank.name from data
            let displayName = tank.name;
            if (window.deviceData) {
                const tankNameField = `tank_${index + 1}_name`;
                if (window.deviceData[tankNameField]) {
                    displayName = window.deviceData[tankNameField];
                }
            }
            
            const tankSlug = slugify(displayName);
            seenTankSlugs.push(tankSlug);
            
            let tankWrapper = document.getElementById(`tank-wrapper-${tankSlug}`);
            
            // If tank HTML doesn't exist, create it
            if (!tankWrapper) {
                tankWrapper = document.createElement('div');
                tankWrapper.className = 'tank-wrapper';
                tankWrapper.id = `tank-wrapper-${tankSlug}`;
                
                const tankTypeClass = displayName.toLowerCase().includes('underground') ? 'underground' : 'overhead';
                
                tankWrapper.innerHTML = `
                    <div class="tank-title">${displayName}</div>
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
            
            tanks.forEach((tank, index) => {
                // Use device tank names if available
                let displayName = tank.name;
                if (window.deviceData) {
                    const tankNameField = `tank_${index + 1}_name`;
                    if (window.deviceData[tankNameField]) {
                        displayName = window.deviceData[tankNameField];
                    }
                }
                
                let p = document.createElement('p');
                p.id = `status-msg-${slugify(displayName)}`;
                
                if (tank.level < 10) {
                    p.textContent = `${displayName}: CRITICAL!`;
                    p.style.color = "red";
                } else if (tank.level < 25) {
                    p.textContent = `${displayName}: Low`;
                    p.style.color = "orange";
                } else if (tank.level > 95) {
                    p.textContent = `${displayName}: FULL`;
                    p.style.color = "blue";
                } else {
                    p.textContent = `${displayName}: ${tank.level}%`;
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
        
        // Add blue color for visibility
        if (statusElement) {
            statusElement.classList.add('connection-status');
        }
    }

    function updateStatusMessage(data) {
        const statusElement = elements.statusMessagesContainer;
        if (statusElement && data) {
            const timestamp = new Date().toLocaleTimeString();
            let statusText = `Last update: ${timestamp}`;
            
            if (data.pump_status !== undefined) {
                statusText += ` | Pump: ${data.pump_status ? 'ON' : 'OFF'}`;
            }
            
            if (data.pump_current !== undefined) {
                statusText += ` | Current: ${data.pump_current}A`;
            }
            
            if (data.system_status) {
                statusText += ` | Status: ${data.system_status}`;
            }
            
            statusElement.textContent = statusText;
        }
    }

    function updateStatusMessages(data) {
        if (!elements.statusMessagesContainer) return;
        
        const messages = [];
        
        // Tank level messages
        for (const [key, value] of Object.entries(data)) {
            if (key.endsWith('_level')) {
                const tankName = getTankNameFromReadingId(key);
                if (value >= 95) {
                    messages.push(`${tankName}: FULL`);
                } else if (value < 10) {
                    messages.push(`${tankName}: CRITICAL!`);
                } else if (value < 25) {
                    messages.push(`${tankName}: Low`);
                } else {
                    messages.push(`${tankName}: ${value}%`);
                }
            }
        }
        
        // System status
        if (data.system_status) {
            messages.push(`System: ${data.system_status}`);
        }
        
        // Pump status
        if (data.pump_status !== undefined) {
            messages.push(`Pump: ${data.pump_status ? 'ON' : 'OFF'}`);
        }
        
        // Current status
        if (data.pump_current !== undefined && window.deviceData) {
            const current = data.pump_current;
            const overloadThreshold = window.deviceData.overload_current_amps || 15;
            const dryRunThreshold = window.deviceData.dry_run_current_amps || 2;
            
            if (current > overloadThreshold) {
                messages.push(`Current: OVERLOAD (${current.toFixed(1)}A)`);
            } else if (current < dryRunThreshold && data.pump_status) {
                messages.push(`Current: DRY RUN (${current.toFixed(1)}A)`);
            } else {
                messages.push(`Current: ${current.toFixed(1)}A`);
            }
        }
        
        // Update status messages container
        elements.statusMessagesContainer.innerHTML = messages.map(msg => `<p>${msg}</p>`).join('');
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