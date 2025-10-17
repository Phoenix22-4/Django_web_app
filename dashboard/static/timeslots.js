// Expandable Timeslots JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize timeslot toggles
    initializeTimeslotToggles();
    
    // Load existing automation rules
    loadAutomationRules();
});

function initializeTimeslotToggles() {
    document.querySelectorAll('.timeslot-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const slot = this.getAttribute('data-slot');
            const form = document.querySelector(`.timeslot-form[data-slot="${slot}"]`);
            
            if (form.classList.contains('hidden')) {
                // Expand
                form.classList.remove('hidden');
                this.textContent = '-';
                this.classList.add('expanded');
            } else {
                // Collapse
                form.classList.add('hidden');
                this.textContent = '+';
                this.classList.remove('expanded');
            }
        });
    });
}

function loadAutomationRules() {
    // Load existing automation rules from the server
    fetch('/api/device_data/{{ device.device_id }}/')
        .then(response => response.json())
        .then(data => {
            if (data.automation_rules) {
                populateTimeslots(data.automation_rules);
            }
        })
        .catch(error => {
            console.error('Error loading automation rules:', error);
        });
}

function populateTimeslots(rules) {
    rules.forEach((rule, index) => {
        const slot = index + 1;
        const form = document.querySelector(`.timeslot-form[data-slot="${slot}"]`);
        
        if (form) {
            form.querySelector('.rule-name').value = rule.name || '';
            form.querySelector('.start-time').value = rule.start_time || '';
            form.querySelector('.end-time').value = rule.end_time || '';
            form.querySelector('.tank-select').value = rule.tank || '';
            form.querySelector('.min-level').value = rule.min_level || '';
            form.querySelector('.max-level').value = rule.max_level || '';
        }
    });
}

// Save timeslot rule
function saveTimeslotRule(slot) {
    const form = document.querySelector(`.timeslot-form[data-slot="${slot}"]`);
    const ruleName = form.querySelector('.rule-name').value;
    const startTime = form.querySelector('.start-time').value;
    const endTime = form.querySelector('.end-time').value;
    const tankSelect = form.querySelector('.tank-select').value;
    const minLevel = form.querySelector('.min-level').value;
    const maxLevel = form.querySelector('.max-level').value;
    
    if (!ruleName || !startTime || !endTime || !tankSelect || !minLevel || !maxLevel) {
        alert('Please fill in all fields');
        return;
    }
    
    // Send to backend
    fetch('/api/save_rule/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            slot: slot,
            rule_name: ruleName,
            start_time: startTime,
            end_time: endTime,
            tank: tankSelect,
            min_level: minLevel,
            max_level: maxLevel
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Rule saved successfully!');
            // Collapse the form
            const toggle = document.querySelector(`.timeslot-toggle[data-slot="${slot}"]`);
            const form = document.querySelector(`.timeslot-form[data-slot="${slot}"]`);
            form.classList.add('hidden');
            toggle.textContent = '+';
            toggle.classList.remove('expanded');
        } else {
            alert('Error saving rule: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error saving rule:', error);
        alert('Error saving rule. Please try again.');
    });
}

// Delete timeslot rule
function deleteTimeslotRule(slot) {
    if (!confirm('Are you sure you want to delete this rule?')) {
        return;
    }
    
    fetch('/api/delete_rule/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            slot: slot
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Rule deleted successfully!');
            // Clear the form
            const form = document.querySelector(`.timeslot-form[data-slot="${slot}"]`);
            form.querySelector('.rule-name').value = '';
            form.querySelector('.start-time').value = '';
            form.querySelector('.end-time').value = '';
            form.querySelector('.tank-select').value = '';
            form.querySelector('.min-level').value = '';
            form.querySelector('.max-level').value = '';
        } else {
            alert('Error deleting rule: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error deleting rule:', error);
        alert('Error deleting rule. Please try again.');
    });
}

// Add event listeners for save and cancel buttons
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.save-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const slot = this.closest('.timeslot').getAttribute('data-slot');
            saveTimeslotRule(slot);
        });
    });
    
    document.querySelectorAll('.cancel-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const slot = this.closest('.timeslot').getAttribute('data-slot');
            const form = document.querySelector(`.timeslot-form[data-slot="${slot}"]`);
            const toggle = document.querySelector(`.timeslot-toggle[data-slot="${slot}"]`);
            
            // Collapse the form
            form.classList.add('hidden');
            toggle.textContent = '+';
            toggle.classList.remove('expanded');
        });
    });
});
