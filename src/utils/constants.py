"""Constants used throughout the application."""

from enum import IntEnum, StrEnum


class OptionalField(StrEnum):
    WEAPON_POWER = 'Weapon Power'
    WEAPON_LIFESTEAL = 'Weapon Lifesteal'
    ATTACK_SPEED = 'Attack Speed'
    RELOAD_SPEED = 'Reload Speed'
    MOVE_SPEED = 'Move Speed'
    CRITICAL_DAMAGE = 'Critical Damage'
    MELEE_DAMAGE = 'Melee Damage'
    MAX_AMMO = 'Max Ammo'
    COOLDOWN_REDUCTION = 'Cooldown Reduction'
    ABILITY_POWER = 'Ability Power'
    ABILITY_LIFESTEAL = 'Ability Lifesteal'
    ARMOR = 'Armor'
    SHIELDS = 'Shields'
    HEALTH = 'Health'


class RequiredField(StrEnum):
    PRICE = 'Price'
    ADJUSTMENT = 'Adjustment'
    EFFECT_VALUE = 'Effect Value'
    EFFECTS = 'Effects'
    FAVORITE = 'Favorite'
    CATEGORY = 'Category'


class UIConstant(IntEnum):
    CARD_WIDTH = 280
    CARD_PADDING = 4
    DEFAULT_COLUMNS = 3
    MIN_WINDOW_WIDTH = 350
    MIN_WINDOW_HEIGHT = 600
    SIDEBAR_WIDTH = 400


class GameConstant(IntEnum):
    MIN_BUDGET = 3500
    MAX_ITEMS = 6


# Optional fields that can be added to items
# OPTIONAL_FIELDS = [
#     'Weapon Power',
#     'Weapon Lifesteal',
#     'Attack Speed',
#     'Reload Speed',
#     'Move Speed',
#     'Critical Damage',
#     'Melee Damage',
#     'Max Ammo',
#     'Cooldown Reduction',
#     'Ability Power',
#     'Ability Lifesteal',
#     'Armor',
#     'Shields',
#     'Health'
# ]

# Required fields for all items
# REQUIRED_FIELDS = [
#     'Price',
#     'Adjustment',
#     'Effect Value',
#     'Effects',
#     'Favorite',
#     'Category'
# ]

# UI Constants
# CARD_WIDTH = 280  # Width of item cards in grid view
# CARD_PADDING = 4  # Padding between cards
# DEFAULT_COLUMNS = 3  # Default number of columns in grid view
# MIN_WINDOW_WIDTH = 350  # Minimum window width
# MIN_WINDOW_HEIGHT = 600  # Minimum window height
# SIDEBAR_WIDTH = 200  # Width of the weights sidebar

# Game Constants
# MIN_BUDGET = 3500  # Minimum budget for optimization
# MAX_ITEMS = 6  # Maximum number of items in a build 

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
SIDEBAR_WIDTH = 400  # Width of the weights sidebar

# Game Constants
MIN_BUDGET = 3500  # Minimum budget for optimization
MAX_ITEMS = 6  # Maximum number of items in a build 

# UI Style Constants
class Style:
    # Colors
    BG_DARK = "#1e1e1e"  # Dark background
    BG_DARKER = "#141414"  # Darker background for contrast
    BG_LIGHTER = "#2d2d2d"  # Lighter background for elements
    FG_MAIN = "#ffffff"  # Main text color
    FG_DIM = "#a0a0a0"  # Dimmed text color
    ACCENT = "#00b894"  # Accent color for important elements
    ACCENT_HOVER = "#00d6a9"  # Accent color when hovering
    ERROR = "#ff5252"  # Error color
    SUCCESS = "#00e676"  # Success color
    BORDER = "#404040"  # Border color

    # Fonts
    FONT_MAIN = ("Segoe UI", 10)
    FONT_TITLE = ("Segoe UI", 12, "bold")
    FONT_LARGE = ("Segoe UI", 18)
    FONT_SMALL = ("Segoe UI", 9)

    # Geometry
    CORNER_RADIUS = 6  # Border radius for elements
    BORDER_WIDTH = 1  # Width of borders
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20

    # Button styles
    BTN_NORMAL = {
        "bg": BG_LIGHTER,
        "fg": FG_MAIN,
        "font": FONT_MAIN,
        "relief": "flat",
        "borderwidth": BORDER_WIDTH,
        "padx": PADDING_MEDIUM,
        "pady": PADDING_SMALL
    }

    BTN_ACCENT = {
        "bg": ACCENT,
        "fg": FG_MAIN,
        "font": FONT_MAIN,
        "relief": "flat",
        "borderwidth": 0,
        "padx": PADDING_MEDIUM,
        "pady": PADDING_SMALL
    }

    # Entry styles
    ENTRY_NORMAL = {
        "bg": BG_DARKER,
        "fg": FG_MAIN,
        "font": FONT_MAIN,
        "relief": "flat",
        "borderwidth": BORDER_WIDTH,
        "insertbackground": FG_MAIN  # Cursor color
    }

    # Frame styles
    FRAME_NORMAL = {
        "bg": BG_DARK,
        "relief": "flat",
        "borderwidth": 0
    }

    FRAME_BORDER = {
        "bg": BG_DARK,
        "relief": "solid",
        "borderwidth": BORDER_WIDTH,
        "highlightbackground": BORDER,
        "highlightthickness": BORDER_WIDTH
    }

    # Label styles
    LABEL_NORMAL = {
        "bg": BG_DARK,
        "fg": FG_MAIN,
        "font": FONT_MAIN
    }

    LABEL_TITLE = {
        "bg": BG_DARK,
        "fg": FG_MAIN,
        "font": FONT_TITLE
    }

    # Treeview styles
    TREEVIEW = {
        "background": BG_DARKER,
        "foreground": FG_MAIN,
        "fieldbackground": BG_DARKER,
        "font": FONT_MAIN
    } 