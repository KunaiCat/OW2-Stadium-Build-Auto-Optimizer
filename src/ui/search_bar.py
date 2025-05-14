"""Search bar component for filtering items."""
import tkinter as tk
from typing import Callable, List
from models.category import Category
from utils.constants import MIN_BUDGET

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
        tk.Label(search_frame, text="Search/Enter Budget:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Search entry
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", self._check_and_optimize)
        
        # Find Best Items button (hidden by default)
        self.find_best_button = tk.Button(search_frame, text="Find Best Items",
                                        command=self._optimize)
        
        # Reset button (hidden by default)
        self.reset_button = tk.Button(search_frame, text="Reset",
                                    command=self._reset)
        
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
        
        # Show/hide optimization button based on budget
        try:
            value = int(search_text)
            if value >= MIN_BUDGET:
                self.find_best_button.pack(side=tk.RIGHT, padx=5)
            else:
                self.find_best_button.pack_forget()
        except ValueError:
            self.find_best_button.pack_forget()
        
        # Get selected categories
        categories = []
        if self.show_weapon.get():
            categories.append(Category.WEAPON)
        if self.show_ability.get():
            categories.append(Category.ABILITY)
        if self.show_survival.get():
            categories.append(Category.SURVIVAL)
        
        # Notify parent
        self.on_search_change(search_text, categories)

    def _check_and_optimize(self, event):
        """Check if search text is a valid budget and optimize if it is."""
        search_text = self.search_var.get().strip()
        try:
            budget = int(search_text)
            if budget >= MIN_BUDGET:
                self._optimize()
        except ValueError:
            pass

    def _optimize(self):
        """Handle optimization request."""
        try:
            budget = int(self.search_var.get().strip())
            if budget < MIN_BUDGET:
                tk.messagebox.showerror("Error", f"Budget must be at least {MIN_BUDGET}")
                return
            self.on_optimize(budget)
            
            # Show reset button
            self.reset_button.pack(side=tk.RIGHT, padx=5)
            
            # Clear search
            self.search_var.set("")
            
        except ValueError:
            tk.messagebox.showerror("Error", 
                                  f"Please enter a valid integer budget (≥{MIN_BUDGET})")

    def _reset(self):
        """Handle reset request."""
        self.on_reset()
        self.reset_button.pack_forget()

    def focus_search(self):
        """Set focus to the search entry."""
        self.search_entry.focus_set() 