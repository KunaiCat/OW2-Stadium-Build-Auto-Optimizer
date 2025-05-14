from enum import Enum

class Category(str, Enum):
    """Enum representing item categories."""
    WEAPON = "Weapon"
    ABILITY = "Ability"
    SURVIVAL = "Survival"
    NONE = "None" 