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
    
    // Live Analytics Data
    let waterUsageChart = null;
    let pumpUsageChart = null;
    let dailyWaterUsage = 0;
    let dailyPumpHours = 0;
    let lastPumpState = false;
    let pumpStartTime = null;
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
        pumpOnBtn: document.getElementById('pumpOnBtn'),
        pumpOffBtn: document.getElementById('pumpOffBtn'),
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
        console.log("🔗 WebSocket URL:", socketURL);
        updateConnectionStatus('websocket', 'Online', 'online');
        updateConnectionStatus('device', 'Connecting...', 'connecting');
        
        // Load device data to get tank names
        loadDeviceData();
    };

    socket.onmessage = function(e) {
        console.log("📡 WebSocket message received");
        try {
            const data = JSON.parse(e.data);
            console.log("📊 Parsed data:", data);
            console.log("🔍 Data keys:", Object.keys(data));
            console.log("⏰ Timestamp:", new Date().toLocaleTimeString());

            // Store data globally for reference
            window.lastData = data;

            updateConnectionStatus('device', 'Online', 'online');

            // Update tanks with live data
            console.log("🔄 Calling updateTankLevelsLive with data:", data);
            updateTankLevelsLive(data);
            
            // Update pump status and animation
            console.log("🔄 Calling updatePumpStatusLive with data:", data);
            updatePumpStatusLive(data);
            
            // Update status messages
            console.log("🔄 Calling updateStatusMessagesLive with data:", data);
            updateStatusMessagesLive(data);
            
            // Update live analytics
            console.log("🔄 Calling updateLiveAnalytics with data:", data);
            updateLiveAnalytics(data);

            console.log("✅ All real-time updates completed successfully");

        } catch (error) {
            console.error("❌ Error processing message:", error);
            updateConnectionStatus('device', 'Error', 'error');
        }
    };

    socket.onclose = function(e) {
        console.log("❌ WebSocket connection closed");
        console.log("🔍 Close code:", e.code, "Reason:", e.reason);
        updateConnectionStatus('websocket', 'Offline', 'offline');
        updateConnectionStatus('device', 'Disconnected', 'offline');
    };

    socket.onerror = function(error) {
        console.error("❌ WebSocket error:", error);
        console.error("🔍 WebSocket URL:", socketURL);
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
                    // Store device data globally for tank name mapping
                    window.deviceData = data.device;
                    
                    // Reinitialize tanks and solenoid valves based on device configuration
                    initializeTanks();
                    initializeSolenoidValves();
                } else {
                    console.log('No device data available, using default tanks');
                    // Initialize with default tanks even if no device data
                    initializeTanks();
                }
            })
            .catch(error => {
                console.error('Error loading device data:', error);
                // Initialize with default tanks even if there's an error
                initializeTanks();
            });
    }

    // --- TANK INITIALIZATION ---
    function initializeTanks() {
        console.log('🔧 INITIALIZING TANK SYSTEM...');
        console.log('🔍 Looking for tanks-wrapper element...');
        
        if (!elements.tanksWrapper) {
            console.error('❌ ERROR: tanks-wrapper element not found!');
            console.error('💡 Make sure the HTML contains: <div id="tanks-wrapper">');
            return;
        }
        
        console.log('✅ tanks-wrapper element found:', elements.tanksWrapper);
        
        // Clear existing tanks
        elements.tanksWrapper.innerHTML = '';
        
        // Initialize empty tank configuration
        window.tankConfigs = [];
        
        // Create tanks from Django admin configuration
        console.log('🔍 Checking window.tankConfig:', window.tankConfig);
        console.log('🔍 Type of window.tankConfig:', typeof window.tankConfig);
        
        if (window.tankConfig && Array.isArray(window.tankConfig) && window.tankConfig.length > 0) {
            console.log('🏗️ Creating tanks from Django admin configuration...');
            window.tankConfig.forEach((tankConfig, index) => {
                console.log(`📦 Creating tank ${index + 1}:`, tankConfig);
                createTankFromAdminConfig(tankConfig);
            });
        } else {
            console.log('ℹ️ No tank configuration found - tanks will be created dynamically from WebSocket data');
            console.log('🔍 Available window properties:', Object.keys(window).filter(key => key.includes('tank')));
        }
        
        console.log('✅ Tank system initialized');
        
        // Initialize live analytics charts
        initializeLiveAnalytics();
    }
    
    // --- LIVE ANALYTICS INITIALIZATION ---
    function initializeLiveAnalytics() {
        console.log('📊 Initializing live analytics charts...');
        
        // Initialize water usage chart
        const waterCtx = document.getElementById('water-usage-chart');
        if (waterCtx) {
            waterUsageChart = new Chart(waterCtx, {
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
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Hours'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Liters'
                            },
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
        
        // Initialize pump usage chart
        const pumpCtx = document.getElementById('pump-usage-chart');
        if (pumpCtx) {
            pumpUsageChart = new Chart(pumpCtx, {
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
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Hours'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Hours'
                            },
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
        
        console.log('✅ Live analytics charts initialized');
        
        // Reset daily data at midnight
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
    
    // --- UPDATE LIVE ANALYTICS ---
    function updateLiveAnalytics(data) {
        if (!data) return;
        
        const currentHour = new Date().getHours();
        
        // Update water usage (estimate based on pump usage and tank levels)
        if (data.pump_status && lastPumpState !== data.pump_status) {
            if (data.pump_status && !lastPumpState) {
                // Pump turned on
                pumpStartTime = new Date();
                console.log('💧 Pump turned ON - starting water usage tracking');
            } else if (!data.pump_status && lastPumpState) {
                // Pump turned off
                if (pumpStartTime) {
                    const pumpDuration = (new Date() - pumpStartTime) / 1000 / 60; // minutes
                    const estimatedWaterUsage = pumpDuration * 2; // 2 liters per minute estimate
                    dailyWaterUsage += estimatedWaterUsage;
                    
                    // Update chart
                    if (waterUsageChart) {
                        waterUsageChart.data.datasets[0].data[currentHour] += estimatedWaterUsage;
                        waterUsageChart.update('none');
                    }
                    
                    console.log(`💧 Pump ran for ${pumpDuration.toFixed(1)} minutes, estimated ${estimatedWaterUsage.toFixed(1)}L used`);
                }
            }
            lastPumpState = data.pump_status;
        }
        
        // Update pump usage hours
        if (data.pump_status) {
            const pumpUsageMinutes = 1; // 1 minute intervals
            dailyPumpHours += pumpUsageMinutes / 60;
            
            if (pumpUsageChart) {
                pumpUsageChart.data.datasets[0].data[currentHour] += pumpUsageMinutes / 60;
                pumpUsageChart.update('none');
            }
        }
        
        console.log(`📊 Daily Stats - Water: ${dailyWaterUsage.toFixed(1)}L, Pump: ${dailyPumpHours.toFixed(2)}H`);
    }
    
    // --- SCHEDULE MIDNIGHT RESET ---
    function scheduleMidnightReset() {
        const now = new Date();
        const midnight = new Date(now);
        midnight.setHours(24, 0, 0, 0);
        
        const msUntilMidnight = midnight.getTime() - now.getTime();
        
        setTimeout(() => {
            resetDailyAnalytics();
            scheduleMidnightReset(); // Schedule next reset
        }, msUntilMidnight);
        
        console.log(`⏰ Daily analytics reset scheduled for midnight (${msUntilMidnight / 1000 / 60} minutes)`);
    }
    
    // --- RESET DAILY ANALYTICS ---
    function resetDailyAnalytics() {
        console.log('🔄 Resetting daily analytics data...');
        
        dailyWaterUsage = 0;
        dailyPumpHours = 0;
        lastPumpState = false;
        pumpStartTime = null;
        
        // Reset chart data
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
        console.log('🏗️ createTankFromAdminConfig called with:', tankConfig);
        
        const readingId = tankConfig.data_key;
        const tankName = tankConfig.name;
        const capacity = tankConfig.capacity || 500;
        
        console.log(`📦 Creating tank: ${tankName} (${readingId}) with capacity: ${capacity}L`);
        
        // Get next available slot
        const slot = window.tankConfigs.length + 1;
        
        // Create tank configuration
        const newTankConfig = {
            id: readingId,
            name: tankName,
            slot: slot,
            capacity: capacity,
            isSource: false
        };
        
        // Add to global tank configs
        window.tankConfigs.push(newTankConfig);
        
        console.log('🔍 About to call createTankDisplay with:', newTankConfig);
        
        // Create tank display with default level 0
        createTankDisplay(newTankConfig, 0);
        
        console.log(`✅ TANK CREATED FROM ADMIN CONFIG: ${tankName} (${readingId}) - Capacity: ${capacity}L`);
    }
    
    // --- CREATE TANK DISPLAY ---
    function createTankDisplay(tankConfig, level = 0) {
        console.log('🏗️ createTankDisplay called with:', tankConfig, 'level:', level);
        
        if (!elements.tanksWrapper) {
            console.error("❌ ERROR: tanks-wrapper element not found in HTML");
            return;
        }
        
        const { id: readingId, name: tankName, slot, capacity, isSource } = tankConfig;
        
        // Create tank HTML element
        const tankDiv = document.createElement('div');
        tankDiv.className = 'flex flex-col items-center';
        const sourceIndicator = isSource ? ' (Source)' : '';
        
        // Calculate liters remaining from level and capacity
        const litersRemaining = Math.round((level / 100) * capacity);
        
        tankDiv.innerHTML = `
            <div class="text-center font-semibold mb-1" style="color: #000000;">${tankName}${sourceIndicator}</div>
            <div id="tank-level-text-${slot}" class="text-center text-2xl font-bold mb-1" style="color: #000000;">${level}%</div>
            <div id="tank-volume-text-${slot}" class="text-center text-sm mb-2" style="color: #666666;">${litersRemaining}L remaining</div>
            <div class="tank-container">
                <div id="water-${slot}" class="water"></div>
            </div>
        `;
        
        // Add to tanks wrapper
        elements.tanksWrapper.appendChild(tankDiv);
        
        // Update tank level immediately
        updateTankLevel(readingId, level);
        
        // Recreate status messages
        createTankStatusMessages();
        
        console.log(`✅ TANK DISPLAY CREATED: ${tankName} (${readingId}) at ${level}%`);
    }
    
    // --- UPDATE EXISTING TANK FROM WEBSOCKET DATA ---
    function updateExistingTankFromData(readingId, level) {
        // Validate input data
        if (!readingId || typeof level !== 'number' || level < 0 || level > 100) {
            console.error(`❌ ERROR: Invalid tank data - readingId: ${readingId}, level: ${level}`);
            console.error("💡 Expected: readingId (string), level (number 0-100)");
            return;
        }
        
        // Check if tank exists (must be configured in Django admin)
        const existingTank = window.tankConfigs.find(tank => tank.id === readingId);
        if (existingTank) {
            console.log(`🔄 Updating existing tank: ${existingTank.name} (${readingId}) to ${level}%`);
            // Update existing tank level
            updateTankLevel(readingId, level);
        } else {
            console.log(`ℹ️ Tank ${readingId} not configured in admin - skipping update`);
            console.log(`💡 Only admin-configured tanks can receive WebSocket updates`);
        }
    }
    
    // --- UPDATE INDIVIDUAL TANK LEVEL ---
    function updateTankLevel(readingId, level) {
        const tank = window.tankConfigs.find(t => t.id === readingId);
        if (!tank) {
            console.error(`❌ ERROR: Tank ${readingId} not found for update`);
            console.error("💡 Available tanks:", window.tankConfigs.map(t => t.id));
            return;
        }
        
        // Validate level data
        if (typeof level !== 'number' || level < 0 || level > 100) {
            console.error(`❌ ERROR: Invalid level data for ${readingId}: ${level}`);
            console.error("💡 Expected: level (number 0-100)");
            return;
        }
        
        const tankWater = document.getElementById(`water-${tank.slot}`);
        const tankLevelText = document.getElementById(`tank-level-text-${tank.slot}`);
        
        if (tankWater && tankLevelText) {
            safeStyleUpdate(tankWater, 'height', `${level}%`);
            safeUpdate(tankLevelText, `${level}%`);
            
            // Set text color to black for better visibility
            tankLevelText.style.color = '#000000';
            
            // Update volume display
            const capacity = tank.capacity || 500;
            const litersRemaining = Math.round((level / 100) * capacity);
            const volumeElement = document.getElementById(`tank-volume-text-${tank.slot}`);
            if (volumeElement) {
                safeUpdate(volumeElement, `${litersRemaining}L remaining`);
            }
            
            // Console confirmation for water level update
            console.log(`💧 WATER LEVEL UPDATE: ${tank.name} (${readingId}): ${level}%`);
        } else {
            console.error(`❌ ERROR: DOM elements not found for tank ${readingId}`);
            console.error(`💡 Looking for: water-${tank.slot}, tank-level-text-${tank.slot}`);
        }
    }
    
    // --- CREATE TANK STATUS MESSAGES ---
    function createTankStatusMessages() {
        const statusContainer = elements.tankStatusMessages;
        if (!statusContainer || !window.tankConfigs) {
            console.error('Tank status messages container not found or no tank configs');
            return;
        }
        
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
        console.log("Updating system data:", data);
        
        // Extract level data and create tanks
        const levelData = [];
        for (const [key, value] of Object.entries(data)) {
            if (key.endsWith('_level')) {
                levelData.push({
                    reading_id: key,
                    level: Math.round(value), // Round to whole number
                    name: getTankNameFromReadingId(key)
                });
            }
        }
        
        console.log("Level data:", levelData);
        
        // Update tanks with level data
        updateTankLevels(levelData);
        
        // Update pump status - check both pump_status and pump_current
        const pumpStatus = data.pump_status !== undefined ? data.pump_status : false;
        const pumpCurrent = data.pump_current !== undefined ? data.pump_current : 0;
        updatePumpStatus(pumpStatus, pumpCurrent);
        
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

    // --- LIVE TANK LEVEL UPDATES (Dynamic System) ---
    function updateTankLevelsLive(data) {
        console.log("🔄 PROCESSING WEBSOCKET DATA:", data);
        console.log("🔍 Function called with data type:", typeof data);
        console.log("🔍 Data is object:", data instanceof Object);
        
        let tanksFound = 0;
        let tanksUpdated = 0;
        let tanksCreated = 0;
        
        // Process all data entries that end with '_level'
        for (const [key, value] of Object.entries(data)) {
            if (key.endsWith('_level') && typeof value === 'number') {
                tanksFound++;
                console.log(`🔍 FOUND TANK DATA: ${key} = ${value}%`);
                
                // Check if tank already exists
                const existingTank = window.tankConfigs.find(tank => tank.id === key);
                
                if (existingTank) {
                    // Update existing tank
                    updateTankLevel(key, value);
                    tanksUpdated++;
                } else {
                    // Tank not configured in admin - skip creation
                    console.log(`ℹ️ Tank ${key} not configured in admin - skipping update`);
                }
            }
        }
        
        // Summary console message
        if (tanksFound > 0) {
            console.log(`📈 TANK PROCESSING SUMMARY: Found ${tanksFound} tanks, Created ${tanksCreated}, Updated ${tanksUpdated}`);
            console.log(`🎯 TANK LEVELS UPDATED: ${tanksUpdated} tanks updated in real-time`);
            if (tanksUpdated > 0) {
                console.log("✅ TANK DRAWINGS: All tank levels and visual representations updated successfully");
            }
        } else {
            console.log("⚠️ NO TANK DATA FOUND: No fields ending with '_level' detected in WebSocket data");
            console.log("💡 Expected format: {overhead_level: 98, underground_level: 82, ...}");
            console.log("🔍 Available data keys:", Object.keys(data));
        }
    }
    
    // --- LIVE PUMP STATUS UPDATES (Based on working code) ---
    function updatePumpStatusLive(data) {
        console.log("🔄 PUMP STATUS UPDATE: Processing live pump data");
        console.log("📊 Pump data received:", {
            pump_status: data.pump_status,
            pump_current: data.pump_current
        });
        
        const pumpIsOn = data.pump_status || false;
        const pumpCurrent = data.pump_current || 0;
        
        console.log(`🔧 PUMP STATUS: ${pumpIsOn ? 'ON' : 'OFF'}, Current: ${pumpCurrent}A`);
        
        // Update pump status text
        const pumpStatusText = document.getElementById('pump-status-text');
        const pumpCurrentText = document.getElementById('pump-current-text');
        const pumpSvg = document.getElementById('pump-svg');
        const pumpToggleBtn = document.getElementById('pump-toggle-btn');
        
        if (pumpStatusText) {
            safeUpdate(pumpStatusText, pumpIsOn ? "ON" : "OFF");
            // Add color coding
            pumpStatusText.style.color = pumpIsOn ? '#10b981' : '#ef4444';
            pumpStatusText.style.fontWeight = 'bold';
        }
        
        if (pumpCurrentText) {
            safeUpdate(pumpCurrentText, `${pumpCurrent.toFixed(1)}A`);
            // Add color coding based on current
            pumpCurrentText.style.color = pumpCurrent > 2.0 ? '#10b981' : '#ef4444';
            pumpCurrentText.style.fontWeight = 'bold';
        }
        
        // Update pump button to reflect current state
        if (pumpToggleBtn) {
            safeUpdate(pumpToggleBtn, pumpIsOn ? "Turn OFF" : "Turn ON");
            // Update button colors
            pumpToggleBtn.className = pumpIsOn ? 
                'bg-red-600 text-white font-bold py-2 px-4 rounded-lg w-32 transition-colors' : 
                'bg-green-600 text-white font-bold py-2 px-4 rounded-lg w-32 transition-colors';
        }
        
        // Update pump animation - THIS IS THE KEY FOR THE ANIMATION
        if (pumpSvg) {
            safeClassToggle(pumpSvg, 'pump-on', pumpIsOn);
            safeClassToggle(pumpSvg, 'pump-off', !pumpIsOn);
            
            // Add active class for animation
            safeClassToggle(pumpSvg, 'active', pumpIsOn);
            safeClassToggle(pumpSvg, 'online', pumpIsOn);
            safeClassToggle(pumpSvg, 'offline', !pumpIsOn);
            
            console.log(`🎬 PUMP ANIMATION: ${pumpIsOn ? 'STARTED' : 'STOPPED'} - Classes applied: active=${pumpIsOn}, online=${pumpIsOn}`);
        }
        
        // Update pump motor animation
        const pumpMotor = document.getElementById('pump-motor');
        if (pumpMotor) {
            safeClassToggle(pumpMotor, 'active', pumpIsOn);
            safeClassToggle(pumpMotor, 'online', pumpIsOn);
            safeClassToggle(pumpMotor, 'offline', !pumpIsOn);
        }
        
        // Update pump status in status messages
        const pumpStatusMsg = document.querySelector('#pump-status-message span');
        if (pumpStatusMsg) {
            safeUpdate(pumpStatusMsg, pumpIsOn ? "ON" : "OFF");
            pumpStatusMsg.style.color = pumpIsOn ? '#10b981' : '#ef4444';
        }
        
        const currentStatusMsg = document.querySelector('#current-status-message span');
        if (currentStatusMsg) {
            safeUpdate(currentStatusMsg, `${pumpCurrent.toFixed(1)}A`);
            currentStatusMsg.style.color = pumpCurrent > 2.0 ? '#10b981' : '#ef4444';
            console.log(`⚡ CURRENT STATUS: ${pumpCurrent.toFixed(1)}A - Color: ${pumpCurrent > 2.0 ? 'green' : 'red'}`);
        }
        
        console.log("✅ SYSTEM STATUS: All status messages updated with real-time data");
        
        console.log(`Pump status: ${pumpIsOn ? 'ON' : 'OFF'}, Current: ${pumpCurrent}A`);
    }
    
    // --- LIVE STATUS MESSAGES (Dynamic System) ---
    function updateStatusMessagesLive(data) {
        console.log("🔄 SYSTEM STATUS UPDATE: Processing live status data");
        console.log("📊 Status data received:", {
            pump_status: data.pump_status,
            pump_current: data.pump_current,
            system_status: data.system_status,
            mode: data.mode
        });
        
        // Update tank status messages dynamically
        if (window.tankConfigs) {
            window.tankConfigs.forEach(tank => {
                const level = data[tank.id] || 0;
                const statusMsgId = `tank-status-msg-${tank.slot}`;
                const statusMsg = document.getElementById(statusMsgId);
                
                if (statusMsg) {
                    if (tank.isSource) {
                        // Source tank status
                        if (level < 10) {
                            statusMsg.textContent = `${tank.name}: CRITICAL!`;
                            statusMsg.style.color = "red";
                        } else if (level < 25) {
                            statusMsg.textContent = `${tank.name}: Low`;
                            statusMsg.style.color = "orange";
                        } else {
                            statusMsg.textContent = `${tank.name}: ${level}%`;
                            statusMsg.style.color = "";
                        }
                    } else {
                        // Secondary tank status
                        if (level >= 95) {
                            statusMsg.textContent = `${tank.name}: FULL`;
                            statusMsg.style.color = "blue";
                        } else {
                            statusMsg.textContent = `${tank.name}: ${level}%`;
                            statusMsg.style.color = "";
                        }
                    }
                }
            });
        }
        
        // Update safety status based on source tank
        const safetyStatusMsg = document.getElementById('safety-status-message');
        if (safetyStatusMsg && window.tankConfigs) {
            const sourceTank = window.tankConfigs.find(tank => tank.isSource);
            if (sourceTank) {
                const sourceLevel = data[sourceTank.id] || 0;
                if (sourceLevel < 10) {
                    safetyStatusMsg.textContent = `SOURCE TANK CRITICAL (${sourceLevel}%) - PUMP OFF`;
                    safetyStatusMsg.classList.remove('hidden');
                } else if (data.pump_status && data.pump_current < 2.0) {
                    safetyStatusMsg.textContent = `DRY RUN DETECTED (${data.pump_current.toFixed(1)}A) - PUMP OFF`;
                    safetyStatusMsg.classList.remove('hidden');
                } else {
                    safetyStatusMsg.classList.add('hidden');
                }
            }
        }
    }
    
    // --- HELPER FUNCTIONS (Based on working code) ---
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

    // --- PUMP STATUS UPDATES ---
    function updatePumpStatus(isOn, current) {
        pumpIsOn = isOn;
        simulatedCurrent = current;
        
        console.log(`Pump status: ${isOn ? 'ON' : 'OFF'}, Current: ${current}A`);
        
        if (elements.pumpSvg) {
            elements.pumpSvg.classList.toggle('pump-on', isOn);
            elements.pumpSvg.classList.toggle('pump-off', !isOn);
            
            // Add visual animation
            if (isOn) {
                elements.pumpSvg.style.animation = 'pumpRotate 2s linear infinite';
            } else {
                elements.pumpSvg.style.animation = 'none';
            }
        }
        
        if (elements.pumpStatusText) {
            elements.pumpStatusText.innerText = isOn ? 'ON' : 'OFF';
            elements.pumpStatusText.style.color = isOn ? '#10b981' : '#ef4444';
            elements.pumpStatusText.style.fontWeight = 'bold';
            elements.pumpStatusText.style.fontSize = '1.2rem';
        }
        
        if (elements.pumpStatusMsg) {
            elements.pumpStatusMsg.innerText = isOn ? 'ON' : 'OFF';
            elements.pumpStatusMsg.className = isOn ? 'font-bold text-green-400' : 'font-bold text-red-400';
            elements.pumpStatusMsg.style.fontSize = '1.1rem';
        }
        
        if (elements.currentStatusMsg) {
            elements.currentStatusMsg.innerText = `${current.toFixed(1)}A`;
            elements.currentStatusMsg.style.color = current > 2.0 ? '#10b981' : '#ef4444';
            elements.currentStatusMsg.style.fontWeight = 'bold';
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

    // --- MANUAL BUTTON UI (Now handled by live updates) ---
    function updateManualButtonUI() {
        // This function is now handled by updatePumpStatusLive()
        // The button state is updated automatically with live data
    }

    // --- SOLENOID TOGGLE HANDLER ---
    function handleSolenoidToggle(solenoidIndex, solenoidName) {
        const currentState = solenoidStates[solenoidIndex] || false;
        const newState = !currentState;
        
        solenoidStates[solenoidIndex] = newState;
        
        // Send command via WebSocket to AWS IoT Core
        if (socket && socket.readyState === WebSocket.OPEN) {
            const command = newState ? 'SOLENOID_ON' : 'SOLENOID_OFF';
            socket.send(JSON.stringify({
                command: command,
                solenoid_index: solenoidIndex,
                solenoid_name: solenoidName
            }));
            console.log(`🔧 Sending solenoid command to AWS IoT Core: ${command} for ${solenoidName}`);
        } else {
            console.error('❌ WebSocket not connected, cannot send solenoid command');
        }
        
        console.log(`Solenoid ${solenoidIndex} (${solenoidName}) ${newState ? 'ON' : 'OFF'}`);
    }

    // --- MODE MANAGEMENT ---
    function setMode(newMode) {
        currentMode = newMode;
        manualOverride = false;
        
        console.log(`Setting mode to: ${newMode}`);
        
        if (elements.modeAutoBtn && elements.modeTimeslotBtn) {
            // Reset both buttons
            elements.modeAutoBtn.classList.remove('mode-btn-active', 'bg-gray-600');
            elements.modeTimeslotBtn.classList.remove('mode-btn-active', 'bg-gray-600');
            
            // Set active button
            if (newMode === 'auto') {
                elements.modeAutoBtn.classList.add('mode-btn-active');
                elements.modeAutoBtn.style.backgroundColor = '#10b981';
                elements.modeAutoBtn.style.color = 'white';
                elements.modeTimeslotBtn.style.backgroundColor = '#6b7280';
                elements.modeTimeslotBtn.style.color = '#d1d5db';
            } else {
                elements.modeTimeslotBtn.classList.add('mode-btn-active');
                elements.modeTimeslotBtn.style.backgroundColor = '#10b981';
                elements.modeTimeslotBtn.style.color = 'white';
                elements.modeAutoBtn.style.backgroundColor = '#6b7280';
                elements.modeAutoBtn.style.color = '#d1d5db';
            }
        }

        if (elements.timeslotControls) {
            elements.timeslotControls.classList.toggle('hidden', newMode !== 'timeslot');
        }
    }

    // --- STATUS MESSAGE UPDATES ---
    function updateStatusMessages(data) {
        if (!elements.safetyStatusMsg) return;
        
        // Safety status checks
        const overheadLevel = data.overhead_level || 0;
        const undergroundLevel = data.underground_level || 0;
        const pumpCurrent = data.pump_current || 0;
        const pumpStatus = data.pump_status || false;
        
        // Check for low source tank (underground)
        if (undergroundLevel < 10) {
            elements.safetyStatusMsg.innerText = `SOURCE TANK LOW (${undergroundLevel}%) - PUMP OFF`;
            elements.safetyStatusMsg.classList.remove('hidden');
        } else if (pumpStatus && pumpCurrent < 2.0) {
            elements.safetyStatusMsg.innerText = `DRY RUN DETECTED (${pumpCurrent.toFixed(1)}A) - PUMP OFF`;
            elements.safetyStatusMsg.classList.remove('hidden');
        } else {
            elements.safetyStatusMsg.classList.add('hidden');
        }

        // Mode status
        if (elements.modeStatusMsg) {
            if (manualOverride) {
                elements.modeStatusMsg.innerText = "Manual Override";
            } else {
                elements.modeStatusMsg.innerText = currentMode.charAt(0).toUpperCase() + currentMode.slice(1);
            }
        }
        
        // Update tank status messages
        const tankStatusContainer = document.getElementById('tank-status-messages');
        if (tankStatusContainer) {
            let tankStatusHtml = '';
            
            // Show overhead tank status
            if (overheadLevel !== undefined) {
                const statusColor = overheadLevel > 80 ? 'text-green-400' : overheadLevel > 50 ? 'text-yellow-400' : 'text-red-400';
                tankStatusHtml += `<div class="${statusColor}">Overhead: ${overheadLevel}%</div>`;
            }
            
            // Show underground tank status
            if (undergroundLevel !== undefined) {
                const statusColor = undergroundLevel > 80 ? 'text-green-400' : undergroundLevel > 50 ? 'text-yellow-400' : 'text-red-400';
                tankStatusHtml += `<div class="${statusColor}">Underground: ${undergroundLevel}%</div>`;
            }
            
            tankStatusContainer.innerHTML = tankStatusHtml;
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
        
        // Pump control buttons
        if (elements.pumpOnBtn) {
            elements.pumpOnBtn.addEventListener('click', () => controlPump(true));
        }
        if (elements.pumpOffBtn) {
            elements.pumpOffBtn.addEventListener('click', () => controlPump(false));
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
        // Check if source tank is available and has sufficient water
        if (window.lastData && window.tankConfigs) {
            const sourceTank = window.tankConfigs.find(tank => tank.isSource);
            if (sourceTank) {
                const sourceLevel = window.lastData[sourceTank.id] || 0;
                if (sourceLevel < 10) {
                    console.log('❌ Cannot turn on pump: Source tank level too low');
                    return;
                }
            }
        }
        
        // Get current pump status from live data
        const currentPumpStatus = window.lastData ? window.lastData.pump_status : false;
        const newPumpStatus = !currentPumpStatus;
        
        // Send command via WebSocket to AWS IoT Core
        if (socket && socket.readyState === WebSocket.OPEN) {
            const command = newPumpStatus ? 'PUMP_ON' : 'PUMP_OFF';
            socket.send(JSON.stringify({command: command}));
            console.log(`${command} command sent`);
        } else {
            console.error('❌ WebSocket not connected, cannot send command');
        }
        
        console.log(`Pump command sent: ${newPumpStatus ? 'ON' : 'OFF'}`);
    }

    function controlPump(turnOn) {
        console.log(`🎛️ PUMP CONTROL: ${turnOn ? 'TURNING ON' : 'TURNING OFF'}`);
        
        // Check if source tank is available and has sufficient water (only for turning on)
        if (turnOn && window.lastData && window.tankConfigs) {
            const sourceTank = window.tankConfigs.find(tank => tank.isSource);
            if (sourceTank) {
                const sourceLevel = window.lastData[sourceTank.id] || 0;
                if (sourceLevel < 10) {
                    console.log('❌ Cannot turn on pump: Source tank level too low');
                    alert('Cannot turn on pump: Source tank level too low (less than 10%)');
                    return;
                }
            }
        }
        
        // Send command via WebSocket to AWS IoT Core
        if (socket && socket.readyState === WebSocket.OPEN) {
            const command = turnOn ? 'PUMP_ON' : 'PUMP_OFF';
            socket.send(JSON.stringify({command: command}));
            console.log(`📡 ${command} command sent via WebSocket`);
        } else {
            console.error('❌ WebSocket not connected, cannot send command');
            alert('Cannot send command: WebSocket not connected');
        }
        
        console.log(`✅ Pump ${turnOn ? 'ON' : 'OFF'} command sent`);
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

    // --- SOLENOID VALVES CREATION ---
    function createSolenoidValves() {
        // Get solenoid names from Django template data
        const solenoidNames = window.solenoidNames || [];
        const solenoidValvesSection = document.getElementById('solenoid-valves-section');
        const solenoidValvesContainer = document.getElementById('solenoid-valves-container');
        
        if (!solenoidValvesSection || !solenoidValvesContainer) {
            console.log('Solenoid valve elements not found');
            return;
        }
        
        if (solenoidNames.length === 0) {
            solenoidValvesSection.classList.add('hidden');
            return;
        }
        
        solenoidValvesSection.classList.remove('hidden');
        solenoidValvesContainer.innerHTML = '';
        
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
            solenoidValvesContainer.appendChild(solenoidDiv);
        });
        
        console.log(`Created ${solenoidNames.length} solenoid valves`);
    }

    // --- INITIALIZATION ---
    setupEventListeners();
    initializeCharts();
    
    // Initialize tanks immediately (don't wait for device data)
    initializeTanks();
    
    // Create solenoid valves
    createSolenoidValves();
    
    // Store socket globally for other functions
    window.socket = socket;
});