"""Validation utilities for the application."""
from typing import Tuple, Optional


def validate_item_input(
    name: str,
    price: str,
    adjustment: str,
    effect_value: str
) -> Tuple[bool, Optional[str]]:
    """Validate input values for an item.
    
    Args:
        name: Item name
        price: Item price as string
        adjustment: Adjustment value as string
        effect_value: Effect value as string
        
    Returns:
        Tuple containing:
        - bool: True if validation passed
        - str or None: Error message if validation failed, None if passed
    """
    # Validate name
    if not name.strip():
        return False, "Name is required"
    
    # Validate price
    try:
        price_val = int(price)
        if price_val <= 0:
            return False, "Price must be a positive integer"
    except ValueError:
        return False, "Price must be a valid integer"
    
    # Validate adjustment
    try:
        adjustment_val = int(adjustment)
        if adjustment_val < 0:
            return False, "Adjustment must be a non-negative integer"
    except ValueError:
        return False, "Adjustment must be a valid integer"
    
    # Validate effect value
    try:
        effect_value_val = int(effect_value)
        if effect_value_val < 0:
            return False, "Effect Value must be a non-negative integer"
    except ValueError:
        return False, "Effect Value must be a valid integer"
    
    return True, None


def validate_weight_input(value: str) -> Tuple[bool, Optional[float]]:
    """Validate a weight input value.
    
    Args:
        value: Weight value as string
        
    Returns:
        Tuple containing:
        - bool: True if validation passed
        - float or None: Parsed float value if passed, None if failed
    """
    try:
        float_val = float(value)
        return True, float_val
    except ValueError:
        return False, None


def round_to_nearest_fraction(value: float) -> float:
    """Round a number to the nearest third, quarter, or twentieth.
    
    Args:
        value: Number to round
        
    Returns:
        Rounded value
    """
    # First round to 2 decimal places
    value = round(value, 2)
    
    # Find the nearest third (0.33, 0.67, 1.00, 1.33, etc)
    thirds = round(value * 3) / 3
    
    # Find the nearest quarter (0.25, 0.50, 0.75, 1.00, etc)
    quarters = round(value * 4) / 4
    
    # Find the nearest twentieth (0.05, 0.10, 0.15, etc)
    twentieths = round(value * 20) / 20
    
    # Find which one is closest to the original value
    options = [thirds, quarters, twentieths]
    differences = [abs(value - opt) for opt in options]
    closest = options[differences.index(min(differences))]
    
    return round(closest, 2) 