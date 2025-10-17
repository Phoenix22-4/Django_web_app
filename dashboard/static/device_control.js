// dashboard/static/device_control.js
class DeviceController {
    constructor(deviceId) {
        this.deviceId = deviceId;
        this.isConnected = false;
        this.pumpStatus = false;
        this.tankData = [];
        this.automationRules = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDeviceData();
        this.startWebSocketConnection();
    }

    setupEventListeners() {
        // Pump control buttons
        const pumpOnBtn = document.getElementById('pump-on-btn');
        const pumpOffBtn = document.getElementById('pump-off-btn');
        
        if (pumpOnBtn) {
            pumpOnBtn.addEventListener('click', () => this.controlPump(true));
        }
        
        if (pumpOffBtn) {
            pumpOffBtn.addEventListener('click', () => this.controlPump(false));
        }

        // Automation rule form
        const ruleForm = document.getElementById('automation-rule-form');
        if (ruleForm) {
            ruleForm.addEventListener('submit', (e) => this.saveAutomationRule(e));
        }

        // Delete rule buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-rule-btn')) {
                const ruleId = e.target.dataset.ruleId;
                this.deleteAutomationRule(ruleId);
            }
        });

        // Test notification button
        const testNotificationBtn = document.getElementById('test-notification-btn');
        if (testNotificationBtn) {
            testNotificationBtn.addEventListener('click', () => this.testNotification());
        }
    }

    async loadDeviceData() {
        try {
            const response = await fetch(`/api/device_data/${this.deviceId}/`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateDeviceDisplay(data);
            } else {
                console.error('Failed to load device data:', data.error);
            }
        } catch (error) {
            console.error('Error loading device data:', error);
        }
    }

    updateDeviceDisplay(data) {
        // Update pump status
        this.pumpStatus = data.device.pump_present;
        this.updatePumpDisplay();

        // Update tank data
        if (data.readings && data.readings.length > 0) {
            const latestReading = data.readings[0];
            this.tankData = latestReading.tank_data;
            this.updateTankDisplay();
        }

        // Update automation rules
        this.automationRules = data.automation_rules;
        this.updateAutomationRulesDisplay();

        // Update connection status
        this.isConnected = data.shadow_data ? true : false;
        this.updateConnectionStatus();
    }

    updatePumpDisplay() {
        const pumpStatusElement = document.getElementById('pump-status');
        const pumpOnBtn = document.getElementById('pump-on-btn');
        const pumpOffBtn = document.getElementById('pump-off-btn');

        if (pumpStatusElement) {
            pumpStatusElement.textContent = this.pumpStatus ? 'ON' : 'OFF';
            pumpStatusElement.className = this.pumpStatus ? 'status-on' : 'status-off';
        }

        if (pumpOnBtn) {
            pumpOnBtn.disabled = this.pumpStatus;
        }

        if (pumpOffBtn) {
            pumpOffBtn.disabled = !this.pumpStatus;
        }
    }

    updateTankDisplay() {
        const tankContainer = document.getElementById('tank-container');
        if (!tankContainer) return;

        tankContainer.innerHTML = '';
        
        this.tankData.forEach(tank => {
            const tankElement = document.createElement('div');
            tankElement.className = 'tank-item';
            tankElement.innerHTML = `
                <div class="tank-name">${tank.name}</div>
                <div class="tank-level">
                    <div class="level-bar">
                        <div class="level-fill" style="width: ${tank.level}%"></div>
                    </div>
                    <div class="level-text">${tank.level}%</div>
                </div>
            `;
            tankContainer.appendChild(tankElement);
        });
    }

    updateAutomationRulesDisplay() {
        const rulesContainer = document.getElementById('automation-rules-container');
        if (!rulesContainer) return;

        rulesContainer.innerHTML = '';
        
        this.automationRules.forEach(rule => {
            const ruleElement = document.createElement('div');
            ruleElement.className = 'automation-rule-item';
            ruleElement.innerHTML = `
                <div class="rule-header">
                    <h4>${rule.name}</h4>
                    <button class="delete-rule-btn" data-rule-id="${rule.id}">Delete</button>
                </div>
                <div class="rule-details">
                    <p><strong>Time:</strong> ${rule.start_time} - ${rule.end_time}</p>
                    <p><strong>Monitor Tank:</strong> ${rule.monitor_tank_name}</p>
                    <p><strong>Level Range:</strong> ${rule.min_level}% - ${rule.max_level}%</p>
                    <p><strong>Status:</strong> ${rule.enabled ? 'Enabled' : 'Disabled'}</p>
                </div>
            `;
            rulesContainer.appendChild(ruleElement);
        });
    }

    updateConnectionStatus() {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = this.isConnected ? 'Connected' : 'Disconnected';
            statusElement.className = this.isConnected ? 'status-connected' : 'status-disconnected';
        }
    }

    async controlPump(pumpOn) {
        try {
            const response = await fetch('/api/pump_control/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device_id: this.deviceId,
                    pump_on: pumpOn
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.pumpStatus = pumpOn;
                this.updatePumpDisplay();
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error controlling pump:', error);
            this.showNotification('Failed to control pump', 'error');
        }
    }

    async saveAutomationRule(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const ruleData = {
            device_id: this.deviceId,
            name: formData.get('rule_name'),
            start_time: formData.get('start_time'),
            end_time: formData.get('end_time'),
            monitor_tank_name: formData.get('monitor_tank'),
            min_level: parseInt(formData.get('min_level')),
            max_level: parseInt(formData.get('max_level')),
            enabled: formData.get('enabled') === 'on'
        };

        try {
            const response = await fetch('/api/save_rule/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(ruleData)
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
                event.target.reset();
                this.loadDeviceData(); // Reload to show new rule
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error saving rule:', error);
            this.showNotification('Failed to save rule', 'error');
        }
    }

    async deleteAutomationRule(ruleId) {
        if (!confirm('Are you sure you want to delete this automation rule?')) {
            return;
        }

        try {
            const response = await fetch('/api/delete_rule/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device_id: this.deviceId,
                    rule_id: ruleId
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
                this.loadDeviceData(); // Reload to remove deleted rule
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error deleting rule:', error);
            this.showNotification('Failed to delete rule', 'error');
        }
    }

    async testNotification() {
        try {
            const response = await fetch('/api/test_notification/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('Error testing notification:', error);
            this.showNotification('Failed to send test notification', 'error');
        }
    }

    startWebSocketConnection() {
        // WebSocket connection for real-time updates
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/dashboard/${this.deviceId}/`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus();
            
            // Reconnect after 5 seconds
            setTimeout(() => {
                this.startWebSocketConnection();
            }, 5000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'device_data':
                this.updateDeviceDisplay(data.data);
                break;
            case 'pump_status':
                this.pumpStatus = data.pump_status;
                this.updatePumpDisplay();
                break;
            case 'tank_data':
                this.tankData = data.tank_data;
                this.updateTankDisplay();
                break;
            case 'notification':
                this.showNotification(data.message, data.level || 'info');
                break;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Public methods for external use
    getDeviceId() {
        return this.deviceId;
    }

    getPumpStatus() {
        return this.pumpStatus;
    }

    getTankData() {
        return this.tankData;
    }

    getAutomationRules() {
        return this.automationRules;
    }

    isDeviceConnected() {
        return this.isConnected;
    }
}

// Initialize device controller when page loads
document.addEventListener('DOMContentLoaded', () => {
    const deviceId = document.body.dataset.deviceId;
    if (deviceId) {
        window.deviceController = new DeviceController(deviceId);
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DeviceController;
}
