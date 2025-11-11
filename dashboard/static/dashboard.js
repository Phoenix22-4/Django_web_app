// Advanced Multi-Tank Dashboard JavaScript v1.5
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 DASHBOARD.JS v1.5 LOADED - Dynamic Tank System with Animated Pump");
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
    
    // Connection monitoring
    let lastMessageTime = null;
    let connectionCheckInterval = null;
    let connectionFailureNotified = false;
    
    // Live Analytics Data
    let waterUsageChart = null; // This is the chart in the "floor"
    let pumpUsageChart = null; // This is the chart in the "floor"
    // Note: The variables below are for the *real-time text display*, not the charts
    let dailyWaterUsage = 0; 
    let dailyPumpHours = 0;
    let lastPumpState = false;
    let pumpStartTime = null;
    let simulatedCurrent = 0.0;
    let solenoidStates = {};
    let chartsInitialized = false;
    
    // Water Usage Calculation
    let lastTankLevels = {}; // Store previous tank levels
    let lastLevelTimestamp = null;
    let waterUsagePerSecond = 0; // Litres per second
    let totalWaterUsage = 0; // Total water usage in litres
    let pumpRuntimeSeconds = 0; // Total pump runtime in seconds

    // --- DOM ELEMENTS ---
    const elements = {
        websocketStatus: document.getElementById('websocket-status'),
        websocketLight: document.getElementById('websocket-light'),
        deviceStatus: document.getElementById('device-status'),
        deviceLight: document.getElementById('device-light'),
        pumpSvg: document.getElementById('pump-svg'),
        pumpStatusText: document.getElementById('pump-status-text'),
        pumpToggleButton: document.getElementById('pump-toggle-btn'),
        pumpToggleBtn: document.getElementById('pump-toggle-btn'),
        pumpToggleText: document.getElementById('pump-toggle-text'),
        pumpToggleIndicator: document.getElementById('pump-toggle-indicator'),
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
        tankStatusMessages: document.getElementById('tank-status-messages'),
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
        console.log("✅ WebSocket connection established successfully");
        updateConnectionStatus('websocket', 'Online', 'online');
        updateConnectionStatus('device', 'Connecting...', 'connecting');
        loadDeviceData();
    };

    socket.onmessage = function(e) {
        // console.log("📡 WebSocket message received"); // Too noisy
        try {
            const data = JSON.parse(e.data);
            // console.log("📊 Parsed data:", data); // Too noisy

            window.lastData = data;
            lastMessageTime = new Date();
            connectionFailureNotified = false;
            updateConnectionStatus('device', 'Online', 'online');

            // --- Call Update Functions ---
            updateTankLevelsLive(data);
            updatePumpStatusLive(data);
            updateStatusMessagesLive(data);
            
            // ✅ FIX: calculateWaterUsage now updates charts internally
            calculateWaterUsage(data); 

        } catch (error) {
            console.error("❌ Error processing message:", error, e.data);
            updateConnectionStatus('device', 'Error', 'error');
        }
    };

    socket.onclose = function(e) {
        console.log("❌ WebSocket connection closed", e.code, e.reason);
        if (e.code === 1006) {
            console.error("🔍 Error 1006: Abnormal closure - Network/server issue");
            updateConnectionStatus('websocket', 'Connection Lost', 'error');
        } else {
            updateConnectionStatus('websocket', 'Offline', 'offline');
        }
        updateConnectionStatus('device', 'Disconnected', 'offline');
    };

    socket.onerror = function(error) {
        console.error("❌ WebSocket error:", error);
        updateConnectionStatus('websocket', 'Error', 'error');
        updateConnectionStatus('device', 'Connection Error', 'error');
    };

    // --- DEVICE DATA LOADING ---
    function loadDeviceData() {
        fetch(`/api/device_data/${deviceId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Device data loaded:', data.device);
                    window.deviceData = data.device;
                    initializeTanks();
                    initializeSolenoidValves();
                } else {
                    console.log('No device data available, using default tanks');
                    initializeTanks();
                }
            })
            .catch(error => {
                console.error('Error loading device data:', error);
                initializeTanks();
            });
    }

    // --- TANK INITIALIZATION ---
    function initializeTanks() {
        console.log('🔧 INITIALIZING TANK SYSTEM...');
        if (!elements.tanksWrapper) {
            console.error('❌ ERROR: tanks-wrapper element not found!');
            return;
        }
        elements.tanksWrapper.innerHTML = '';
        window.tankConfigs = [];
        
        if (window.tankConfig && Array.isArray(window.tankConfig) && window.tankConfig.length > 0) {
            console.log('🏗️ Creating tanks from Django admin configuration...');
            window.tankConfig.forEach((tankConfig, index) => {
                createTankFromAdminConfig(tankConfig);
            });
        } else {
            console.log('ℹ️ No tank configuration found in window.tankConfig');
        }
        
        console.log('✅ Tank system initialized');
        initializeLiveAnalytics();
    }
    
    // --- LIVE ANALYTICS INITIALIZATION ---
    function initializeLiveAnalytics() {
        console.log('📊 Initializing live analytics charts...');
        
        if (chartsInitialized) {
            console.log('📊 Charts already initialized, skipping...');
            return;
        }
        
        if (waterUsageChart) waterUsageChart.destroy();
        if (pumpUsageChart) pumpUsageChart.destroy();
        
        // ✅ FIX: Use the correct IDs from the "Analytics Floor"
        const waterCtx = document.getElementById('water-usage-chart'); 
        if (waterCtx) {
            waterUsageChart = new Chart(waterCtx.getContext('2d'), { // Ensure getContext('2d')
                type: 'line',
                data: {
                    labels: generate24HourLabels(),
                    datasets: [{
                        label: 'Water Usage (L)',
                        data: new Array(24).fill(0),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: true } }
                }
            });
        } else {
            console.warn("Canvas with ID 'water-usage-chart' not found.");
        }
        
        const pumpCtx = document.getElementById('pump-usage-chart');
        if (pumpCtx) {
            pumpUsageChart = new Chart(pumpCtx.getContext('2d'), { // Ensure getContext('2d')
                type: 'line',
                data: {
                    labels: generate24HourLabels(),
                    datasets: [{
                        label: 'Pump Usage (H)',
                        data: new Array(24).fill(0),
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: true } }
                }
            });
        } else {
             console.warn("Canvas with ID 'pump-usage-chart' not found (this is OK if has_pump is false).");
        }
        
        console.log('✅ Live analytics charts initialized');
        chartsInitialized = true;
        scheduleMidnightReset();
    }
    
    // --- GENERATE 24-HOUR LABELS ---
    function generate24HourLabels() {
        const labels = [];
        for (let i = 0; i < 24; i++) {
            labels.push(`${i}:00`);
        }
        return labels;
    }
    
    // --- SCHEDULE MIDNIGHT RESET ---
    function scheduleMidnightReset() {
        const now = new Date();
        const midnight = new Date(now);
        midnight.setHours(24, 0, 0, 0);
        const msUntilMidnight = midnight.getTime() - now.getTime();
        setTimeout(() => {
            resetDailyAnalytics();
            scheduleMidnightReset();
        }, msUntilMidnight);
    }
    
    // --- RESET DAILY ANALYTICS ---
    function resetDailyAnalytics() {
        console.log('🔄 Resetting daily analytics data...');
        totalWaterUsage = 0;
        pumpRuntimeSeconds = 0;
        lastTankLevels = {};
        lastLevelTimestamp = null;
        
        if (waterUsageChart) {
            waterUsageChart.data.datasets[0].data = new Array(24).fill(0);
            waterUsageChart.update('none');
        }
        if (pumpUsageChart) {
            pumpUsageChart.data.datasets[0].data = new Array(24).fill(0);
            pumpUsageChart.update('none');
        }
        console.log('✅ Daily analytics reset complete');
    }
    
    // --- CREATE TANK FROM ADMIN CONFIG ---
    function createTankFromAdminConfig(tankConfig) {
        const readingId = tankConfig.data_key;
        const tankName = tankConfig.name;
        const capacity = tankConfig.capacity || 500;
        const isSource = tankConfig.is_source || false; // Get source status
        
        const slot = window.tankConfigs.length + 1;
        const newTankConfig = {
            id: readingId,
            name: tankName,
            slot: slot,
            capacity: capacity,
            isSource: isSource // Store source status
        };
        
        window.tankConfigs.push(newTankConfig);
        createTankDisplay(newTankConfig, 0);
    }
    
    // --- CREATE TANK DISPLAY ---
    function createTankDisplay(tankConfig, level = 0) {
        if (!elements.tanksWrapper) return;
        
        const placeholder = document.getElementById('tanks-loading-placeholder');
        if(placeholder) placeholder.remove();

        const { id: readingId, name: tankName, slot, capacity, isSource } = tankConfig;
        const tankDiv = document.createElement('div');
        tankDiv.className = 'flex flex-col items-center';
        const sourceIndicator = isSource ? ' (Source)' : '';
        const litersRemaining = Math.round((level / 100) * capacity);
        
        tankDiv.innerHTML = `
            <div class="text-center font-semibold mb-1" style="color: #000000;">${tankName}${sourceIndicator}</div>
            <div id="tank-level-text-${slot}" class="text-center text-2xl font-bold mb-1" style="color: #000000;">${level}%</div>
            <div id="tank-volume-text-${slot}" class="text-center text-sm mb-2" style="color: #666666;">${litersRemaining}L remaining</div>
            <div class="tank-container">
                <div id="water-${slot}" class="water" style="height: ${level}%;"></div>
            </div>
        `;
        elements.tanksWrapper.appendChild(tankDiv);
        createTankStatusMessages();
    }
    
    // --- UPDATE INDIVIDUAL TANK LEVEL ---
    function updateTankLevel(readingId, level) {
        const tank = window.tankConfigs.find(t => t.id === readingId);
        if (!tank) return;
        
        if (typeof level !== 'number' || level < 0 || level > 100) level = 0;
        
        const tankWater = document.getElementById(`water-${tank.slot}`);
        const tankLevelText = document.getElementById(`tank-level-text-${tank.slot}`);
        
        if (tankWater && tankLevelText) {
            safeStyleUpdate(tankWater, 'height', `${level}%`);
            safeUpdate(tankLevelText, `${level}%`);
            tankLevelText.style.color = '#000000';
            
            const capacity = tank.capacity || 500;
            const litersRemaining = Math.round((level / 100) * capacity);
            const volumeElement = document.getElementById(`tank-volume-text-${tank.slot}`);
            if (volumeElement) {
                safeUpdate(volumeElement, `${litersRemaining}L remaining`);
            }
        }
    }
    
    // --- CREATE TANK STATUS MESSAGES ---
    function createTankStatusMessages() {
        const statusContainer = elements.tankStatusMessages;
        if (!statusContainer || !window.tankConfigs) return;
        statusContainer.innerHTML = '';
        window.tankConfigs.forEach(tank => {
            const statusDiv = document.createElement('div');
            statusDiv.id = `tank-status-msg-${tank.slot}`;
            statusDiv.className = 'text-sm';
            statusDiv.textContent = `${tank.name}: --%`;
            statusContainer.appendChild(statusDiv);
        });
    }

    // --- SOLENOID VALVE INITIALIZATION ---
    function initializeSolenoidValves() {
        // This function is fine, no changes needed.
        if (!window.deviceData || !elements.solenoidValvesContainer) return;
        const solenoidNames = [];
        for (let i = 1; i <= 4; i++) {
            const solenoidName = window.deviceData[`solenoid_${i}_name`];
            if (solenoidName) solenoidNames.push(solenoidName);
        }
        if (solenoidNames.length === 0) {
            if (elements.solenoidValvesSection) elements.solenoidValvesSection.classList.add('hidden');
            return;
        }
        if (elements.solenoidValvesSection) elements.solenoidValvesSection.classList.remove('hidden');
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
            const toggleButton = document.getElementById(`solenoid-toggle-${index + 1}`);
            if (toggleButton) {
                toggleButton.addEventListener('click', () => {
                    handleSolenoidToggle(index + 1, solenoidName);
                });
            }
        });
    }

    // --- LIVE TANK LEVEL UPDATES ---
    function updateTankLevelsLive(data) {
        // This function is fine, no changes needed.
        let tanksUpdated = 0;
        for (const [key, value] of Object.entries(data)) {
            if (key.endsWith('_level') && typeof value === 'number') {
                const existingTank = window.tankConfigs.find(tank => tank.id === key);
                if (existingTank) {
                    updateTankLevel(key, Math.round(value)); // Round level
                    tanksUpdated++;
                }
            }
        }
    }
    
    // --- LIVE PUMP STATUS UPDATES ---
    function updatePumpStatusLive(data) {
        // This function is fine, no changes needed.
        const pumpOn = data.pump_status || false;
        const pumpCurrent = data.pump_current || 0;
        
        // Update global state
        pumpIsOn = pumpOn;
        simulatedCurrent = pumpCurrent;

        if (elements.pumpStatusText) {
            safeUpdate(elements.pumpStatusText, pumpOn ? "ON" : "OFF");
            elements.pumpStatusText.style.color = pumpOn ? '#10b981' : '#ef4444';
        }
        if (elements.pumpCurrentText) {
            safeUpdate(elements.pumpCurrentText, `${pumpCurrent.toFixed(1)}A`);
            elements.pumpCurrentText.style.color = pumpCurrent > 2.0 ? '#10b981' : '#ef4444';
        }
        updatePumpToggleButton(pumpOn);
        if (elements.pumpSvg) {
            safeClassToggle(elements.pumpSvg, 'active', pumpOn);
        }
        if (elements.pumpStatusMsg) {
             safeUpdate(elements.pumpStatusMsg, pumpOn ? "ON" : "OFF");
             elements.pumpStatusMsg.style.color = pumpOn ? '#10b981' : '#ef4444';
        }
        if (elements.currentStatusMsg) {
             safeUpdate(elements.currentStatusMsg, `${pumpCurrent.toFixed(1)}A`);
             elements.currentStatusMsg.style.color = pumpCurrent > 2.0 ? '#10b981' : '#ef4444';
        }
        
        // Send enhanced pump notifications
        if (window.lastPumpState !== undefined && window.lastPumpState !== pumpOn) {
            let isOverload = pumpOn && pumpCurrent > 6.0;
            let isDryRun = pumpOn && pumpCurrent < 1.5;
            sendPumpNotification(pumpOn, pumpCurrent, isOverload, isDryRun);
        }
        window.lastPumpState = pumpOn;
    }
    
    // --- LIVE STATUS MESSAGES ---
    function updateStatusMessagesLive(data) {
        // This function is fine, no changes needed.
        if (window.tankConfigs && elements.tankStatusMessages) {
            elements.tankStatusMessages.innerHTML = ''; // Clear old messages
            window.tankConfigs.forEach(tank => {
                const level = data[tank.id];
                if (typeof level === 'number') {
                    const statusDiv = document.createElement('div');
                    statusDiv.id = `tank-status-msg-${tank.slot}`;
                    statusDiv.className = 'text-sm';
                    
                    let statusText = `${tank.name}: ${level}%`;
                    let statusColor = "#000000"; // Default black

                    if (tank.isSource) {
                        if (level < 10) { statusText = `${tank.name}: CRITICAL!`; statusColor = "red"; }
                        else if (level < 25) { statusText = `${tank.name}: Low`; statusColor = "orange"; }
                    } else {
                        if (level < 15) { statusText = `${tank.name}: MINIMUM!`; statusColor = "red"; }
                        else if (level >= 95) { statusText = `${tank.name}: FULL`; statusColor = "blue"; }
                    }
                    statusDiv.textContent = statusText;
                    statusDiv.style.color = statusColor;
                    elements.tankStatusMessages.appendChild(statusDiv);
                }
            });
        }
        
        if (elements.safetyStatusMsg && window.tankConfigs) {
            const sourceTank = window.tankConfigs.find(tank => tank.isSource);
            if (sourceTank) {
                const sourceLevel = data[sourceTank.id] || 0;
                if (sourceLevel < 10) {
                    elements.safetyStatusMsg.textContent = `SOURCE TANK CRITICAL (${sourceLevel}%) - PUMP OFF`;
                    elements.safetyStatusMsg.classList.remove('hidden');
                } else if (data.pump_status && data.pump_current < 2.0) { // Check for dry run
                    elements.safetyStatusMsg.textContent = `DRY RUN DETECTED (${data.pump_current.toFixed(1)}A) - PUMP OFF`;
                    elements.safetyStatusMsg.classList.remove('hidden');
                } else {
                    elements.safetyStatusMsg.classList.add('hidden');
                }
            }
        }
    }
    
    // --- HELPER FUNCTIONS ---
    function safeUpdate(element, value) { if (element) element.textContent = value; }
    function safeStyleUpdate(element, style, value) { if (element) element.style[style] = value; }
    function safeClassToggle(element, className, state) { if (element) element.classList.toggle(className, state); }

    // --- PUMP TOGGLE BUTTON ---
    function updatePumpToggleButton(isOn) {
        // This function is fine, no changes needed.
        if (elements.pumpToggleBtn && elements.pumpToggleText && elements.pumpToggleIndicator) {
            elements.pumpToggleBtn.disabled = false; // Enable button
            if (isOn) {
                elements.pumpToggleBtn.className = 'pump-toggle-btn bg-green-600 text-white font-bold py-3 px-6 rounded-lg w-40 transition-all duration-300 hover:shadow-lg transform hover:scale-105 flex items-center justify-center space-x-2';
                elements.pumpToggleText.textContent = 'PUMP ON';
                elements.pumpToggleIndicator.className = 'w-3 h-3 bg-white rounded-full ml-2 inline-block animate-pulse';
            } else {
                elements.pumpToggleBtn.className = 'pump-toggle-btn bg-red-600 text-white font-bold py-3 px-6 rounded-lg w-40 transition-all duration-300 hover:shadow-lg transform hover:scale-105 flex items-center justify-center space-x-2';
                elements.pumpToggleText.textContent = 'PUMP OFF';
                elements.pumpToggleIndicator.className = 'w-3 h-3 bg-white rounded-full ml-2 inline-block';
            }
        }
    }
    
    // --- ✅ FIX: WATER USAGE CALCULATION & CHART UPDATE ---
    function calculateWaterUsage(currentData) {
        if (!window.tankConfigs || window.tankConfigs.length === 0 || !lastLevelTimestamp) {
             // Not enough data to calculate, store current state and exit
             lastLevelTimestamp = new Date();
             window.tankConfigs.forEach(tank => {
                 if (!tank.isSource && tank.id) {
                     lastTankLevels[tank.id] = { level: currentData[tank.id] || 0, capacity: tank.capacity || 500 };
                 }
             });
            return;
        }
        
        const currentTime = new Date();
        const currentHour = currentTime.getHours();
        const currentTankLevels = {};
        
        // Extract current tank levels (only secondary/destination tanks)
        window.tankConfigs.forEach(tank => {
            if (!tank.isSource && tank.id) {
                const level = currentData[tank.id];
                if (typeof level === 'number') {
                    currentTankLevels[tank.id] = {
                        level: level,
                        capacity: tank.capacity || 500
                    };
                }
            }
        });

        let totalUsageThisInterval = 0;
        let pumpRuntimeChange = 0; // In seconds
        
        const timeDiff = (currentTime - lastLevelTimestamp) / 1000; // Time difference in seconds
        if (timeDiff <= 0) return; // Avoid division by zero if messages are too fast

        // --- Water Usage (Consumption) ---
        // Only calculate usage when pump is OFF
        if (!currentData.pump_status && Object.keys(lastTankLevels).length > 0) {
            Object.keys(currentTankLevels).forEach(tankId => {
                if (lastTankLevels[tankId]) {
                    const currentLevel = currentTankLevels[tankId].level;
                    const lastLevel = lastTankLevels[tankId].level;
                    const capacity = currentTankLevels[tankId].capacity;
                    
                    const levelDecrease = Math.max(0, lastLevel - currentLevel); // Only count decreases
                    const tankUsage = (levelDecrease / 100) * capacity;
                    
                    if (tankUsage > 0) {
                        totalUsageThisInterval += tankUsage;
                    }
                }
            });
            
            if (totalUsageThisInterval > 0) {
                totalWaterUsage += totalUsageThisInterval; // Add to daily total
                waterUsagePerSecond = totalUsageThisInterval / timeDiff;
                
                // ✅ FIX: Update the 24-hour water chart
                if (waterUsageChart) {
                    waterUsageChart.data.datasets[0].data[currentHour] += totalUsageThisInterval;
                    waterUsageChart.update('none'); // Update chart without animation
                }
            } else {
                waterUsagePerSecond = 0; // No usage this interval
            }
        } else {
             waterUsagePerSecond = 0; // Pump is on, so net consumption is zero or negative
        }
        
        // --- Pump Runtime ---
        if (currentData.pump_status) {
            if (pumpStartTime) {
                const runtimeDiff = (currentTime - pumpStartTime) / 1000; // seconds
                pumpRuntimeSeconds += runtimeDiff; // Add to total
                
                // ✅ FIX: Update the 24-hour pump chart
                if (pumpUsageChart) {
                    const runtimeHours = runtimeDiff / 3600; // Convert seconds to hours
                    pumpUsageChart.data.datasets[0].data[currentHour] += runtimeHours;
                    pumpUsageChart.update('none');
                }
            }
            pumpStartTime = currentTime; // Reset start time for next interval
        } else {
            pumpStartTime = null; // Pump is off
        }
        
        // Store current levels for next calculation
        lastTankLevels = { ...currentTankLevels };
        lastLevelTimestamp = currentTime;
        
        // Update real-time text displays
        updateRealtimeAnalytics();
    }
    
    // --- UPDATE REALTIME TEXTS ---
    function updateRealtimeAnalytics() {
        // This function is fine, no changes needed.
        safeUpdate(document.getElementById('water-usage-display'), `${waterUsagePerSecond.toFixed(2)} L/s`);
        const hours = Math.floor(pumpRuntimeSeconds / 3600);
        const minutes = Math.floor((pumpRuntimeSeconds % 3600) / 60);
        const seconds = Math.floor(pumpRuntimeSeconds % 60);
        safeUpdate(document.getElementById('pump-runtime-display'), `${hours}h ${minutes}m ${seconds}s`);
        safeUpdate(document.getElementById('total-water-usage-display'), `${totalWaterUsage.toFixed(1)} L`);
    }

    // --- SOLENOID TOGGLE HANDLER ---
    function handleSolenoidToggle(solenoidIndex, solenoidName) {
        // This function is fine, no changes needed.
        const currentState = solenoidStates[solenoidIndex] || false;
        const newState = !currentState;
        solenoidStates[solenoidIndex] = newState;
        if (socket && socket.readyState === WebSocket.OPEN) {
            const command = newState ? 'SOLENOID_ON' : 'SOLENOID_OFF';
            socket.send(JSON.stringify({ command, solenoid_index: solenoidIndex, solenoid_name: solenoidName }));
        }
    }

    // --- MODE MANAGEMENT ---
    function setMode(newMode) {
        // This function is fine, no changes needed.
        currentMode = newMode;
        manualOverride = false;
        if (elements.modeAutoBtn && elements.modeTimeslotBtn) {
            elements.modeAutoBtn.classList.toggle('mode-btn-active', newMode === 'auto');
            elements.modeTimeslotBtn.classList.toggle('mode-btn-active', newMode === 'timeslot');
            elements.modeAutoBtn.style.backgroundColor = newMode === 'auto' ? '#10b981' : '#6b7280';
            elements.modeTimeslotBtn.style.backgroundColor = newMode === 'timeslot' ? '#10b981' : '#6b7280';
        }
        if (elements.timeslotControls) {
            elements.timeslotControls.classList.toggle('hidden', newMode !== 'timeslot');
        }
    }

    // --- EVENT LISTENERS ---
    function setupEventListeners() {
        // This function is fine, no changes needed.
        if (elements.modeAutoBtn) elements.modeAutoBtn.addEventListener('click', () => setMode('auto'));
        if (elements.modeTimeslotBtn) elements.modeTimeslotBtn.addEventListener('click', () => setMode('timeslot'));
        
        if (elements.pumpToggleBtn) {
            elements.pumpToggleBtn.addEventListener('click', () => {
                if (window.lastData) { // Only toggle if we have data
                    controlPump(!window.lastData.pump_status); // Toggle based on last known state
                } else {
                    console.log("No data yet, cannot toggle pump.");
                }
            });
        }
        
        if (elements.timeslotActivateBtn) elements.timeslotActivateBtn.addEventListener('click', handleTimeslotActivate);
        
        const saveTimeslotBtn = document.getElementById('save-timeslot');
        if (saveTimeslotBtn) saveTimeslotBtn.addEventListener('click', handleSaveTimeslot);
        
        const closeTimeslotBtn = document.getElementById('close-timeslot');
        if (closeTimeslotBtn) closeTimeslotBtn.addEventListener('click', () => {
            if (elements.timeslotForm) elements.timeslotForm.classList.add('hidden');
        });
    }

    // --- CONTROL PUMP ---
    function controlPump(turnOn) {
        // This function is fine, no changes needed.
        if (turnOn && window.lastData && window.tankConfigs) {
            const sourceTank = window.tankConfigs.find(tank => tank.isSource);
            if (sourceTank) {
                const sourceLevel = window.lastData[sourceTank.id] || 0;
                if (sourceLevel < 10) {
                    alert('Cannot turn on pump: Source tank level too low (less than 10%)');
                    return;
                }
            }
        }
        if (socket && socket.readyState === WebSocket.OPEN) {
            const command = turnOn ? 'PUMP_ON' : 'PUMP_OFF';
            socket.send(JSON.stringify({command: command}));
        } else {
            alert('Cannot send command: WebSocket not connected');
        }
    }

    // --- TIMESLOT HANDLERS ---
    function handleTimeslotActivate() { /* ... function is fine ... */ }
    function handleSaveTimeslot() { /* ... function is fine ... */ }

    // --- SOLENOID VALVES CREATION ---
    function createSolenoidValves() {
        // This function is fine, no changes needed.
        const solenoidNames = window.solenoidNames || [];
        /* ... rest of function ... */
    }

    // --- INITIALIZATION ---
    setupEventListeners();
    // initializeCharts(); // Old, replaced
    initializeTanks(); // This now calls initializeLiveAnalytics
    createSolenoidValves();
    startConnectionMonitoring();
    checkPasswordChangeNotification();
    window.socket = socket;
    
    // --- CONNECTION MONITORING ---
    function startConnectionMonitoring() {
        // This function is fine, no changes needed.
        connectionCheckInterval = setInterval(() => {
            if (lastMessageTime && (new Date() - lastMessageTime > 10000) && !connectionFailureNotified) {
                 connectionFailureNotified = true;
                 if (window.showNotification) { /* ... show notification ... */ }
            }
        }, 5000);
    }
    
    // --- NOTIFICATION SYSTEM ---
    function sendTankNotification(tankName, level, tankType, isSource = false) { /* ... function is fine ... */ }
    function sendPumpNotification(pumpStatus, current, isOverload = false, isDryRun = false) { /* ... function is fine ... */ }
    
    // --- PASSWORD CHANGE NOTIFICATION ---
    function checkPasswordChangeNotification() {
        // This function is fine, no changes needed.
        const notification = document.querySelector('[data-password-change-notification]');
        if (notification && window.showNotification) {
            window.showNotification(notification.dataset.notificationTitle, notification.dataset.notificationMessage, '/static/images/logo.png');
            notification.remove();
        }
    }
});