// dashboard/static/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");

    // --- 1. Get Elements ---
    const deviceIdElement = document.getElementById('device-id');
    if (!deviceIdElement) {
        console.error("ERROR: Device ID meta tag not found!");
        return;
    }
    const deviceId = deviceIdElement.getAttribute('content');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // --- Sockets ---
    const socketProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socketURL = `${socketProtocol}//${window.location.host}/ws/dashboard/${deviceId}/`;
    console.log(`Connecting to WebSocket: ${socketURL}`);
    const socket = new WebSocket(socketURL);

    // --- Element Selectors ---
    const elements = {
        websocketStatus: document.getElementById('websocket-status'),
        websocketLight: document.getElementById('websocket-light'),
        deviceStatus: document.getElementById('device-status'),
        deviceLight: document.getElementById('device-light'),
        pumpStatusText: document.getElementById('pump-status-text'),
        pumpCurrentText: document.getElementById('pump-current-text'),
        pumpMotor: document.getElementById('pump-motor'),
        pumpLed: document.getElementById('pump-led'),
        pumpOnBtn: document.getElementById('pump-on'),
        pumpOffBtn: document.getElementById('pump-off'),
        autoModeStatus: document.getElementById('auto-mode-status'),
        statusMessageBox: document.getElementById('status-messages-box'),
        tanksContainer: document.querySelector('.tanks-container'),
        // Automation Modal
        modal: document.getElementById('rule-modal'),
        modalTitle: document.getElementById('modal-title'),
        modalForm: document.getElementById('rule-form'),
        modalCancel: document.getElementById('modal-cancel'),
        addRuleBtn: document.getElementById('add-rule-btn'),
        rulesList: document.getElementById('automation-rules-list'),
        // Modal Form Fields
        ruleId: document.getElementById('rule-id'),
        ruleName: document.getElementById('rule-name'),
        ruleStartTime: document.getElementById('rule-start-time'),
        ruleEndTime: document.getElementById('rule-end-time'),
        ruleMonitorTank: document.getElementById('rule-monitor-tank'),
        ruleMinLevel: document.getElementById('rule-min-level'),
        ruleMaxLevel: document.getElementById('rule-max-level')
    };
    
    // --- Chart Context ---
    let pumpChart = null;
    let powerChart = null;

    // --- 2. WebSocket Handlers ---
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

            // --- 1. DYNAMIC TANK UPDATE ---
            if (data.tanks && Array.isArray(data.tanks)) {
                updateDynamicTanks(data.tanks);
            }

            // --- 2. PUMP STATUS (if pump exists) ---
            if (elements.pumpMotor) {
                const pumpIsOn = data.pump_status;
                safeUpdate(elements.pumpStatusText, pumpIsOn ? "ON" : "OFF");
                safeClassToggle(elements.pumpMotor, 'active', pumpIsOn);
                safeClassToggle(elements.pumpMotor, 'online', pumpIsOn);
                safeClassToggle(elements.pumpMotor, 'offline', !pumpIsOn);
                safeClassToggle(elements.pumpLed, 'led-on', pumpIsOn);
                safeClassToggle(elements.pumpLed, 'led-off', !pumpIsOn);
                safeUpdate(elements.pumpCurrentText, `${data.pump_current_amps?.toFixed(1) || '0.0'} A`);
            }

            // --- 3. AUTOMATION & STATUS MESSAGES ---
            safeUpdate(elements.autoModeStatus, data.automation_mode || 'System Auto-Mode');
            updateStatusMessages(data.tanks);

            // --- 4. UPDATE CHARTS (with dummy data for now) ---
            // In a real app, this data would come from a separate API call or be part of the payload
            updatePumpChart([80, 20]); // 80% off, 20% on
            updatePowerChart([0,0,0,0,0, 0.5, 0.5, 0.4, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0.1,0.1,0]);

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

    // --- 3. DYNAMIC TANK UI FUNCTION ---
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

        // Populate tank dropdown in modal
        if (elements.ruleMonitorTank) {
            elements.ruleMonitorTank.innerHTML = ''; // Clear old options
            tanks.forEach(tank => {
                elements.ruleMonitorTank.innerHTML += `<option value="${tank.name}">${tank.name}</option>`;
            });
        }
    }

    function updateStatusMessages(tanks) {
        if (!elements.statusMessageBox) return;
        elements.statusMessageBox.innerHTML = ''; // Clear old messages

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
            elements.statusMessageBox.appendChild(p);
        });
    }

    // --- 4. PUMP CONTROL LISTENERS ---
    if (elements.pumpOnBtn) {
        elements.pumpOnBtn.addEventListener('click', () => {
            socket.send(JSON.stringify({command: 'PUMP_ON'}));
        });
    }
    if (elements.pumpOffBtn) {
        elements.pumpOffBtn.addEventListener('click', () => {
            socket.send(JSON.stringify({command: 'PUMP_OFF'}));
        });
    }

    // --- 5. AUTOMATION MODAL LOGIC ---
    function openRuleModal(rule = null) {
        elements.modalForm.reset(); // Clear the form
        if (rule) {
            // Edit mode
            safeUpdate(elements.modalTitle, 'Edit Automation Rule');
            elements.ruleId.value = rule.id;
            elements.ruleName.value = rule.name;
            elements.ruleStartTime.value = rule.start_time;
            elements.ruleEndTime.value = rule.end_time;
            elements.ruleMonitorTank.value = rule.monitor_tank_name;
            elements.ruleMinLevel.value = rule.min_level;
            elements.ruleMaxLevel.value = rule.max_level;
        } else {
            // Create mode
            safeUpdate(elements.modalTitle, 'Create New Automation Rule');
            elements.ruleId.value = ''; // No ID yet
        }
        elements.modal.classList.remove('hidden');
    }

    function closeRuleModal() {
        elements.modal.classList.add('hidden');
    }

    if (elements.addRuleBtn) elements.addRuleBtn.addEventListener('click', () => openRuleModal());
    if (elements.modalCancel) elements.modalCancel.addEventListener('click', closeRuleModal);

    if (elements.modalForm) {
        elements.modalForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const ruleData = {
                id: elements.ruleId.value || null,
                device_id: deviceId,
                name: elements.ruleName.value,
                start_time: elements.ruleStartTime.value,
                end_time: elements.ruleEndTime.value,
                monitor_tank_name: elements.ruleMonitorTank.value,
                min_level: elements.ruleMinLevel.value,
                max_level: elements.ruleMaxLevel.value,
                enabled: true
            };
            
            try {
                const response = await fetch('/api/save_rule/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                    body: JSON.stringify(ruleData)
                });
                const result = await response.json();
                if (result.status === 'success') {
                    closeRuleModal();
                    // You would ideally refresh the list of rules here
                    window.location.reload(); // Simple way to refresh
                } else {
                    alert('Error saving rule: ' + result.error);
                }
            } catch (err) {
                alert('Network error saving rule.');
            }
        });
    }

    // Add listeners for existing Edit/Delete buttons
    elements.rulesList.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const ruleItem = e.currentTarget.closest('.rule-item');
            // This is complex, as the data is not in the JS. 
            // A full implementation would fetch rule data or embed it in HTML.
            // For now, let's just open the modal in "create" mode.
            openRuleModal();
        });
    });
    
    elements.rulesList.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            if (confirm('Are you sure you want to delete this rule?')) {
                const ruleItem = e.currentTarget.closest('.rule-item');
                const ruleId = ruleItem.dataset.ruleId;
                
                try {
                    const response = await fetch('/api/delete_rule/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                        body: JSON.stringify({ id: ruleId })
                    });
                    const result = await response.json();
                    if (result.status === 'success') {
                        ruleItem.remove(); // Remove from UI
                    } else {
                        alert('Error deleting rule: ' + result.error);
                    }
                } catch (err) {
                    alert('Network error deleting rule.');
                }
            }
        });
    });


    // --- 6. CHART INITIALIZATION ---
    function initCharts() {
        if (document.getElementById('pumpRuntimeChart')) {
            const pumpCtx = document.getElementById('pumpRuntimeChart').getContext('2d');
            pumpChart = new Chart(pumpCtx, {
                type: 'pie',
                data: {
                    labels: ['Off', 'On'],
                    datasets: [{ data: [1, 0], backgroundColor: ['#6c757d', '#28a745'], borderWidth: 2 }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
        
        if (document.getElementById('powerUsageChart')) {
            const powerCtx = document.getElementById('powerUsageChart').getContext('2d');
            powerChart = new Chart(powerCtx, {
                type: 'bar',
                data: {
                    labels: Array.from({length: 24}, (_, i) => `${String(i).padStart(2, '0')}:00`),
                    datasets: [{ label: 'Avg. Current (Amps)', data: Array(24).fill(0), backgroundColor: '#007bff' }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            });
        }
    }
    
    function updatePumpChart(data) {
        if (pumpChart) {
            pumpChart.data.datasets[0].data = data;
            pumpChart.update();
        }
    }
    
    function updatePowerChart(data) {
        if (powerChart) {
            powerChart.data.datasets[0].data = data;
            powerChart.update();
        }
    }
    
    initCharts(); // Create charts on page load
    
    // --- 7. HELPER FUNCTIONS ---
    function safeUpdate(element, value) {
        if (element) element.textContent = value;
    }
    function safeStyleUpdate(element, style, value) {
        if (element) element.style[style] = value;
    }
    function safeClassToggle(element, className, state) {
        if (element) element.classList.toggle(className, state);
    }
    function updateConnectionStatus(type, text, state) {
        const statusElement = type === 'websocket' ? elements.websocketStatus : elements.deviceStatus;
        const lightElement = type === 'websocket' ? elements.websocketLight : elements.deviceLight;
        safeUpdate(statusElement, text);
        if (lightElement) lightElement.className = `status-light ${state}`;
    }
    function slugify(text) {
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')       // Replace spaces with -
            .replace(/[^\w\-]+/g, '')   // Remove all non-word chars
            .replace(/\-\-+/g, '-')     // Replace multiple - with single -
            .replace(/^-+/, '')        // Trim - from start of text
            .replace(/-+$/, '');       // Trim - from end of text
    }
});