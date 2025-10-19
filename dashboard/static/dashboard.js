// Advanced Multi-Tank Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log("Advanced Multi-Tank Dashboard loaded");

    const deviceIdElement = document.getElementById('device-id');
    if (!deviceIdElement) {
        console.error("ERROR: Device ID meta tag not found!");
        return;
    }
    const deviceId = deviceIdElement.getAttribute('content');
    console.log(`Device ID: ${deviceId}`);

    // --- STATE MANAGEMENT ---
    let tankLevels = [];
    let pumpIsOn = false;
    let currentMode = 'auto';
    let manualOverride = false;
    let isTimeslotActive = false;
    let timeslotSettings = { min: 20, max: 95 };
    let simulatedCurrent = 0.0;
    let solenoidStates = {};

    // --- DOM ELEMENTS ---
    const elements = {
        websocketStatus: document.getElementById('websocket-status'),
        websocketLight: document.getElementById('websocket-light'),
        deviceStatus: document.getElementById('device-status'),
        deviceLight: document.getElementById('device-light'),
        pumpSvg: document.getElementById('pump-svg'),
        pumpStatusText: document.getElementById('pump-status-text'),
        pumpToggleButton: document.getElementById('pump-toggle-btn'),
        modeAutoBtn: document.getElementById('mode-auto'),
        modeTimeslotBtn: document.getElementById('mode-timeslot'),
        modeStatusMsg: document.querySelector('#mode-status-message span'),
        pumpStatusMsg: document.querySelector('#pump-status-message span'),
        currentStatusMsg: document.querySelector('#current-status-message span'),
        safetyStatusMsg: document.getElementById('safety-status-message'),
        timeslotControls: document.getElementById('timeslot-controls'),
        timeslotActivateBtn: document.getElementById('timeslot-activate-btn'),
        timeslotForm: document.getElementById('timeslot-form'),
        tanksWrapper: document.getElementById('tanks-wrapper'),
        solenoidValvesSection: document.getElementById('solenoid-valves-section'),
        solenoidValvesContainer: document.getElementById('solenoid-valves-container')
    };

    // Check for missing elements
    Object.entries(elements).forEach(([key, element]) => {
        if (!element) console.warn(`Missing element: ${key}`);
    });

    // --- WEBSOCKET CONNECTION ---
    const socketProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socketURL = `${socketProtocol}//${window.location.host}/ws/dashboard/${deviceId}/`;
    console.log(`Connecting to WebSocket: ${socketURL}`);
    const socket = new WebSocket(socketURL);

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

    // --- DEVICE DATA LOADING ---
    function loadDeviceData() {
        fetch(`/api/device_data/${deviceId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Device data loaded:', data.device);
                    // Store device data globally for tank name mapping
                    window.deviceData = data.device;
                    
                    // Initialize tanks and solenoid valves based on device configuration
                    initializeTanks();
                    initializeSolenoidValves();
                }
            })
            .catch(error => {
                console.error('Error loading device data:', error);
            });
    }

    // --- TANK INITIALIZATION ---
    function initializeTanks() {
        if (!window.deviceData || !elements.tanksWrapper) return;
        
        const tankNames = [];
        for (let i = 1; i <= 4; i++) {
            const tankName = window.deviceData[`tank_${i}_name`];
            if (tankName) {
                tankNames.push(tankName);
            }
        }
        
        elements.tanksWrapper.innerHTML = '';
        
        if (tankNames.length === 0) {
            elements.tanksWrapper.innerHTML = '<div class="col-span-2 text-center text-gray-400">No tanks configured</div>';
            return;
        }
        
        tankNames.forEach((tankName, index) => {
            const tankDiv = document.createElement('div');
            tankDiv.className = 'flex flex-col items-center';
            tankDiv.innerHTML = `
                <div class="text-center font-semibold mb-1">${index === 0 ? 'Tank 1 (Source)' : `Tank ${index + 1}`}</div>
                <div id="tank-level-text-${index + 1}" class="text-center text-2xl font-bold mb-2">0%</div>
                <div class="tank-container">
                    <div id="water-${index + 1}" class="water"></div>
                </div>
            `;
            elements.tanksWrapper.appendChild(tankDiv);
        });
    }

    // --- SOLENOID VALVE INITIALIZATION ---
    function initializeSolenoidValves() {
        if (!window.deviceData || !elements.solenoidValvesContainer) return;
        
        const solenoidNames = [];
        for (let i = 1; i <= 4; i++) {
            const solenoidName = window.deviceData[`solenoid_${i}_name`];
            if (solenoidName) {
                solenoidNames.push(solenoidName);
            }
        }
        
        if (solenoidNames.length === 0) {
            if (elements.solenoidValvesSection) {
                elements.solenoidValvesSection.classList.add('hidden');
            }
            return;
        }
        
        if (elements.solenoidValvesSection) {
            elements.solenoidValvesSection.classList.remove('hidden');
        }
        
        elements.solenoidValvesContainer.innerHTML = '';
        
        solenoidNames.forEach((solenoidName, index) => {
            const solenoidDiv = document.createElement('div');
            solenoidDiv.className = 'bg-gray-700 p-3 rounded-lg text-center';
            solenoidDiv.innerHTML = `
                <h4 class="font-semibold mb-2">${solenoidName}</h4>
                <div id="solenoid-status-${index + 1}" class="text-sm mb-2">OFF</div>
                <button id="solenoid-toggle-${index + 1}" class="bg-red-600 text-white px-3 py-1 rounded text-sm">
                    Turn ON
                </button>
            `;
            elements.solenoidValvesContainer.appendChild(solenoidDiv);
            
            // Add event listener for solenoid toggle
            const toggleButton = document.getElementById(`solenoid-toggle-${index + 1}`);
            if (toggleButton) {
                toggleButton.addEventListener('click', () => {
                    handleSolenoidToggle(index + 1, solenoidName);
                });
            }
        });
    }

    // --- DYNAMIC SYSTEM DATA UPDATE ---
    function updateDynamicSystemData(data) {
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
        updateTankLevels(levelData);
        
        // Update pump status
        if (data.pump_status !== undefined) {
            updatePumpStatus(data.pump_status, data.pump_current || 0);
        }
        
        // Update solenoid valve data
        if (data.solenoid_data) {
            updateSolenoidValves(data.solenoid_data);
        }
        
        // Update status messages
        updateStatusMessages(data);
        
        // Update charts
        updateCharts(data);
    }

    // --- TANK NAME MAPPING ---
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

    // --- TANK LEVEL UPDATES ---
    function updateTankLevels(tankData) {
        tankData.forEach((tank, index) => {
            const levelElement = document.getElementById(`water-${index + 1}`);
            const percentElement = document.getElementById(`tank-level-text-${index + 1}`);
            
            if (levelElement && percentElement) {
                levelElement.style.height = `${tank.level}%`;
                percentElement.textContent = `${tank.level}%`;
            }
        });
    }

    // --- PUMP STATUS UPDATES ---
    function updatePumpStatus(isOn, current) {
        pumpIsOn = isOn;
        simulatedCurrent = current;
        
        if (elements.pumpSvg) {
            elements.pumpSvg.classList.toggle('pump-on', isOn);
            elements.pumpSvg.classList.toggle('pump-off', !isOn);
        }
        
        if (elements.pumpStatusText) {
            elements.pumpStatusText.innerText = isOn ? 'ON' : 'OFF';
        }
        
        if (elements.pumpStatusMsg) {
            elements.pumpStatusMsg.innerText = isOn ? 'ON' : 'OFF';
            elements.pumpStatusMsg.className = isOn ? 'font-bold text-green-400' : 'font-bold text-red-400';
        }
        
        if (elements.currentStatusMsg) {
            elements.currentStatusMsg.innerText = `${current.toFixed(1)}A`;
        }
        
        updateManualButtonUI();
    }

    // --- SOLENOID VALVE UPDATES ---
    function updateSolenoidValves(solenoidData) {
        solenoidData.forEach((solenoid, index) => {
            const statusElement = document.getElementById(`solenoid-status-${index + 1}`);
            const toggleButton = document.getElementById(`solenoid-toggle-${index + 1}`);
            
            if (statusElement && toggleButton) {
                statusElement.textContent = solenoid.isOn ? 'ON' : 'OFF';
                toggleButton.textContent = solenoid.isOn ? 'Turn OFF' : 'Turn ON';
                toggleButton.className = solenoid.isOn ? 
                    'bg-green-600 text-white px-3 py-1 rounded text-sm' : 
                    'bg-red-600 text-white px-3 py-1 rounded text-sm';
            }
        });
    }

    // --- MANUAL BUTTON UI ---
    function updateManualButtonUI() {
        if (elements.pumpToggleButton) {
            elements.pumpToggleButton.innerText = pumpIsOn ? 'Turn OFF' : 'Turn ON';
            elements.pumpToggleButton.classList.toggle('bg-red-600', pumpIsOn);
            elements.pumpToggleButton.classList.toggle('bg-green-600', !pumpIsOn);
        }
    }

    // --- SOLENOID TOGGLE HANDLER ---
    function handleSolenoidToggle(solenoidIndex, solenoidName) {
        const currentState = solenoidStates[solenoidIndex] || false;
        const newState = !currentState;
        
        solenoidStates[solenoidIndex] = newState;
        
        // Send command via WebSocket
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                command: newState ? 'SOLENOID_ON' : 'SOLENOID_OFF',
                solenoid_index: solenoidIndex,
                solenoid_name: solenoidName
            }));
        }
        
        console.log(`Solenoid ${solenoidIndex} (${solenoidName}) ${newState ? 'ON' : 'OFF'}`);
    }

    // --- MODE MANAGEMENT ---
    function setMode(newMode) {
        currentMode = newMode;
        manualOverride = false;
        
        if (elements.modeAutoBtn && elements.modeTimeslotBtn) {
            elements.modeAutoBtn.classList.toggle('mode-btn-active', newMode === 'auto');
            elements.modeAutoBtn.classList.toggle('bg-gray-600', newMode !== 'auto');
            elements.modeTimeslotBtn.classList.toggle('mode-btn-active', newMode === 'timeslot');
            elements.modeTimeslotBtn.classList.toggle('bg-gray-600', newMode !== 'timeslot');
        }

        if (elements.timeslotControls) {
            elements.timeslotControls.classList.toggle('hidden', newMode !== 'timeslot');
        }
    }

    // --- STATUS MESSAGE UPDATES ---
    function updateStatusMessages(data) {
        if (!elements.safetyStatusMsg) return;
        
        // Safety status checks
        const sourceTankOk = data.source_tank_level >= 10; // Assuming source tank is first
        const currentOk = data.pump_current >= 2.0; // Dry run threshold
        
        if (!sourceTankOk) {
            elements.safetyStatusMsg.innerText = "SRC TANK LOW - PUMP OFF";
            elements.safetyStatusMsg.classList.remove('hidden');
        } else if (data.pump_status && !currentOk) {
            elements.safetyStatusMsg.innerText = "DRY RUN - PUMP OFF";
            elements.safetyStatusMsg.classList.remove('hidden');
        } else {
            elements.safetyStatusMsg.classList.add('hidden');
        }

        // Mode status
        if (elements.modeStatusMsg) {
            if (manualOverride) {
                elements.modeStatusMsg.innerText = "Manual";
            } else {
                elements.modeStatusMsg.innerText = currentMode.charAt(0).toUpperCase() + currentMode.slice(1);
            }
        }
    }

    // --- CHART UPDATES ---
    function updateCharts(data) {
        const now = new Date();
        const timeLabel = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
        
        // Update water usage chart
        if (window.waterUsageChart) {
            const totalUsage = data.water_usage || 0;
            window.waterUsageChart.data.labels.push(timeLabel);
            window.waterUsageChart.data.datasets[0].data.push(totalUsage);
            
            // Keep only last 30 data points
            if (window.waterUsageChart.data.labels.length > 30) {
                window.waterUsageChart.data.labels.shift();
                window.waterUsageChart.data.datasets[0].data.shift();
            }
            
            window.waterUsageChart.update();
        }
        
        // Update pump runtime chart
        if (window.pumpRuntimeChart) {
            const runtime = data.pump_runtime || 0;
            window.pumpRuntimeChart.data.labels.push(timeLabel);
            window.pumpRuntimeChart.data.datasets[0].data.push(runtime);
            
            // Keep only last 30 data points
            if (window.pumpRuntimeChart.data.labels.length > 30) {
                window.pumpRuntimeChart.data.labels.shift();
                window.pumpRuntimeChart.data.datasets[0].data.shift();
            }
            
            window.pumpRuntimeChart.update();
        }
    }

    // --- CONNECTION STATUS UPDATES ---
    function updateConnectionStatus(type, text, state) {
        const statusElement = type === 'websocket' ? elements.websocketStatus : elements.deviceStatus;
        const lightElement = type === 'websocket' ? elements.websocketLight : elements.deviceLight;
        
        if (statusElement) {
            statusElement.textContent = text;
            statusElement.className = `status-text connection-status ${state}`;
        }
        
        if (lightElement) {
            lightElement.className = `status-dot ${state}`;
        }
    }

    // --- EVENT LISTENERS ---
    function setupEventListeners() {
        // Mode buttons
        if (elements.modeAutoBtn) {
            elements.modeAutoBtn.addEventListener('click', () => setMode('auto'));
        }
        if (elements.modeTimeslotBtn) {
            elements.modeTimeslotBtn.addEventListener('click', () => setMode('timeslot'));
        }
        
        // Pump toggle
        if (elements.pumpToggleButton) {
            elements.pumpToggleButton.addEventListener('click', handleManualPumpToggle);
        }
        
        // Timeslot controls
        if (elements.timeslotActivateBtn) {
            elements.timeslotActivateBtn.addEventListener('click', handleTimeslotActivate);
        }
        
        const saveTimeslotBtn = document.getElementById('save-timeslot');
        const closeTimeslotBtn = document.getElementById('close-timeslot');
        
        if (saveTimeslotBtn) {
            saveTimeslotBtn.addEventListener('click', handleSaveTimeslot);
        }
        if (closeTimeslotBtn) {
            closeTimeslotBtn.addEventListener('click', () => {
                if (elements.timeslotForm) {
                    elements.timeslotForm.classList.add('hidden');
                }
            });
        }
    }

    function handleManualPumpToggle() {
        manualOverride = true;
        pumpIsOn = !pumpIsOn;
        updateManualButtonUI();
        
        // Send command via WebSocket
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                command: pumpIsOn ? 'PUMP_ON' : 'PUMP_OFF'
            }));
        }
        
        console.log(`Pump ${pumpIsOn ? 'ON' : 'OFF'} (manual override)`);
    }

    function handleTimeslotActivate() {
        if (!isTimeslotActive) {
            if (elements.timeslotForm) {
                elements.timeslotForm.classList.remove('hidden');
            }
        } else {
            isTimeslotActive = false;
            if (elements.timeslotActivateBtn) {
                elements.timeslotActivateBtn.innerText = 'Deactivated';
                elements.timeslotActivateBtn.classList.replace('timeslot-btn-active', 'timeslot-btn-inactive');
            }
        }
    }

    function handleSaveTimeslot() {
        const minLevelInput = document.getElementById('min-level');
        const maxLevelInput = document.getElementById('max-level');
        
        if (minLevelInput && maxLevelInput) {
            timeslotSettings.min = parseInt(minLevelInput.value) || 20;
            timeslotSettings.max = parseInt(maxLevelInput.value) || 95;
        }
        
        isTimeslotActive = true;
        
        if (elements.timeslotActivateBtn) {
            elements.timeslotActivateBtn.innerText = `Active (Min: ${timeslotSettings.min}%, Max: ${timeslotSettings.max}%)`;
            elements.timeslotActivateBtn.classList.replace('timeslot-btn-inactive', 'timeslot-btn-active');
        }
        
        if (elements.timeslotForm) {
            elements.timeslotForm.classList.add('hidden');
        }
    }

    // --- CHART INITIALIZATION ---
    function initializeCharts() {
        // Water usage chart
        const waterCtx = document.getElementById('waterUsageChart');
        if (waterCtx) {
            window.waterUsageChart = new Chart(waterCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Litres per Second',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    scales: {
                        x: { ticks: { color: '#9ca3af' }, grid: { color: '#374151' } },
                        y: { beginAtZero: true, ticks: { color: '#9ca3af' }, grid: { color: '#374151' } }
                    },
                    plugins: { legend: { labels: { color: '#d1d5db' } } }
                }
            });
        }
        
        // Pump runtime chart
        const pumpCtx = document.getElementById('pumpRuntimeChart');
        if (pumpCtx) {
            window.pumpRuntimeChart = new Chart(pumpCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Seconds Active',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    scales: {
                        x: { ticks: { color: '#9ca3af' }, grid: { color: '#374151' } },
                        y: { beginAtZero: true, ticks: { color: '#9ca3af' }, grid: { color: '#374151' } }
                    },
                    plugins: { legend: { labels: { color: '#d1d5db' } } }
                }
            });
        }
    }

    // --- INITIALIZATION ---
    setupEventListeners();
    initializeCharts();
    
    // Store socket globally for other functions
    window.socket = socket;
});