"""
Automation Rule Logic for AquaSavvy Solution
This module handles user-defined automation rules that override system defaults.
"""
from django.utils import timezone
from .models import Device, AutomationRule, WaterReading


def get_active_rule(device: Device) -> AutomationRule | None:
    """
    Check if any automation rule is currently active for this device.
    Returns the first active rule found, or None if no rules are active.
    """
    active_rules = device.rules.filter(enabled=True)
    for rule in active_rules:
        if rule.is_active_now():
            return rule
    return None


def should_pump_turn_on(device: Device, current_reading: WaterReading) -> tuple[bool, str]:
    """
    Determine if the pump should turn ON based on automation rules or default logic.
    
    Returns:
        tuple: (should_turn_on: bool, reason: str)
    """
    # Check for active automation rule first
    active_rule = get_active_rule(device)
    
    if active_rule:
        # Use rule's logic
        tank_level = _get_tank_level(current_reading, active_rule.destination_tank)
        if tank_level is not None and tank_level <= active_rule.min_level:
            return (True, f"Timeslot Active: {active_rule.name} (ON at {active_rule.min_level}%)")
        else:
            return (False, f"Timeslot Active: {active_rule.name} (waiting for {active_rule.destination_tank} ≤ {active_rule.min_level}%)")
    
    # Default system logic
    underground_level = _get_tank_level(current_reading, "Underground")
    overhead_level = _get_tank_level(current_reading, "Overhead")
    
    # Safety: Don't turn on if underground is too low
    if underground_level is not None and underground_level < 10:
        return (False, "System Auto-Mode (Underground tank too low - dry run protection)")
    
    # Turn on if overhead is low and underground has water
    if overhead_level is not None and overhead_level < 30:
        if underground_level is not None and underground_level > 15:
            return (True, "System Auto-Mode (Overhead low, refilling)")
    
    return (False, "System Auto-Mode (no action needed)")


def should_pump_turn_off(device: Device, current_reading: WaterReading) -> tuple[bool, str]:
    """
    Determine if the pump should turn OFF based on automation rules or default logic.
    
    Returns:
        tuple: (should_turn_off: bool, reason: str)
    """
    # Check for active automation rule first
    active_rule = get_active_rule(device)
    
    if active_rule:
        # Use rule's logic
        tank_level = _get_tank_level(current_reading, active_rule.destination_tank)
        if tank_level is not None and tank_level >= active_rule.max_level:
            return (True, f"Timeslot Active: {active_rule.name} (OFF at {active_rule.max_level}%)")
        else:
            return (False, f"Timeslot Active: {active_rule.name} (filling {active_rule.destination_tank} to {active_rule.max_level}%)")
    
    # Default system logic
    underground_level = _get_tank_level(current_reading, "Underground")
    overhead_level = _get_tank_level(current_reading, "Overhead")
    
    # Safety: Turn off if underground is critically low (dry run protection)
    if underground_level is not None and underground_level < 10:
        return (True, "System Auto-Mode (Dry run protection - underground critically low)")
    
    # Turn off if overhead is full
    if overhead_level is not None and overhead_level >= 95:
        return (True, "System Auto-Mode (Overhead tank full)")
    
    return (False, "System Auto-Mode (pump should continue)")


def get_pump_status_message(device: Device, current_reading: WaterReading) -> str:
    """
    Get a human-readable status message for the current pump state.
    This is displayed on the dashboard to inform the user what mode is active.
    """
    active_rule = get_active_rule(device)
    
    if active_rule:
        tank_level = _get_tank_level(current_reading, active_rule.destination_tank)
        return f"Timeslot Active: {active_rule.name} (ON: {active_rule.min_level}%, OFF: {active_rule.max_level}%) - {active_rule.destination_tank}: {tank_level}%"
    
    if current_reading.pump_mode == "MANUAL":
        return "Manual Mode (User-controlled via dashboard)"
    
    return "System Auto-Mode (Smart automation active)"


def _get_tank_level(reading: WaterReading, tank_name: str) -> int | None:
    """Helper function to get tank level by name from tank_data or legacy fields."""
    # Try new dynamic tank_data first
    if reading.tank_data:
        for tank in reading.tank_data:
            if tank.get('name') == tank_name:
                return tank.get('level')
    
    # Fallback to legacy fields
    if tank_name == "Overhead" and reading.overhead_level is not None:
        return reading.overhead_level
    if tank_name == "Underground" and reading.underground_level is not None:
        return reading.underground_level
    
    return None

