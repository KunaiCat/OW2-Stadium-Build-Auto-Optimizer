"""Search bar component for filtering items."""
import tkinter as tk
from typing import Callable
from models.category import Category
from utils.constants import GameConstant

class SearchBar(tk.Frame):
    """Search bar component with category filters and optimization controls."""

    def __init__(self, parent: tk.Widget,
                 on_search_change: Callable[[str, list], None],
                 on_optimize: Callable[[int], None],
                 on_reset: Callable[[], None]):
        """Initialize the search bar.
        
        Args:
            parent: Parent widget
            on_search_change: Callback for when search/filter criteria change
            on_optimize: Callback for when optimization is requested
            on_reset: Callback for when view reset is requested
        """
        super().__init__(parent)
        self.on_search_change = on_search_change
        self.on_optimize = on_optimize
        self.on_reset = on_reset
        
        # Category filter variables
        self.show_weapon = tk.BooleanVar(value=True)
        self.show_ability = tk.BooleanVar(value=True)
        self.show_survival = tk.BooleanVar(value=True)
        
        # Search variable
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Search frame
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search label
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Search entry
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Category filter frame
        filter_frame = tk.Frame(self)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Category filter label
        tk.Label(filter_frame, text="Show Categories:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Category checkboxes
        tk.Checkbutton(filter_frame, text="Weapon", variable=self.show_weapon,
                      command=self._on_search_change).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(filter_frame, text="Ability", variable=self.show_ability,
                      command=self._on_search_change).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(filter_frame, text="Survival", variable=self.show_survival,
                      command=self._on_search_change).pack(side=tk.LEFT, padx=5)

    def _on_search_change(self, *args):
        """Handle changes to search text or category filters."""
        search_text = self.search_var.get().strip()
        # Only filter by keywords, no optimization or buttons
        categories = []
        if self.show_weapon.get():
            categories.append(Category.WEAPON)
        if self.show_ability.get():
            categories.append(Category.ABILITY)
        if self.show_survival.get():
            categories.append(Category.SURVIVAL)
        self.on_search_change(search_text, categories) 