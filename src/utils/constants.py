"""Constants used throughout the application."""

# Optional fields that can be added to items
OPTIONAL_FIELDS = [
    'Weapon Power',
    'Weapon Lifesteal',
    'Attack Speed',
    'Reload Speed',
    'Move Speed',
    'Critical Damage',
    'Melee Damage',
    'Max Ammo',
    'Cooldown Reduction',
    'Ability Power',
    'Ability Lifesteal',
    'Armor',
    'Shields',
    'Health'
]

# Required fields for all items
REQUIRED_FIELDS = [
    'Price',
    'Adjustment',
    'Effect Value',
    'Effects',
    'Favorite',
    'Category'
]

# UI Constants
CARD_WIDTH = 280  # Width of item cards in grid view
CARD_PADDING = 4  # Padding between cards
DEFAULT_COLUMNS = 3  # Default number of columns in grid view
MIN_WINDOW_WIDTH = 350  # Minimum window width
MIN_WINDOW_HEIGHT = 600  # Minimum window height
SIDEBAR_WIDTH = 200  # Width of the weights sidebar

# Game Constants
MIN_BUDGET = 3500  # Minimum budget for optimization
MAX_ITEMS = 6  # Maximum number of items in a build 