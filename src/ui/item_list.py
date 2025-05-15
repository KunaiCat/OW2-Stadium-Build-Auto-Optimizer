"""Item list component for displaying items in grid or list view."""
import tkinter as tk
from typing import Dict, Callable, List, Optional
from models.item import Item
from utils.constants import UIConstant, Style

class ItemList(tk.Frame):
    """Component for displaying items in grid or list view."""

    def __init__(self, parent: tk.Widget, on_edit: Callable[[str], None]):
        """Initialize the item list.
        
        Args:
            parent: Parent widget
            on_edit: Callback for when an item is selected for editing
        """
        super().__init__(parent, **Style.FRAME_NORMAL)
        self.on_edit = on_edit
        
        # Find parent window
        self.parent_window = parent
        while self.parent_window and not hasattr(self.parent_window, '_refresh_display'):
            self.parent_window = self.parent_window.master
        
        # Display state
        self.current_columns = UIConstant.DEFAULT_COLUMNS
        self.optimal_items: List[str] = []
        
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Frame to hold items
        self.items_frame = tk.Frame(self, **Style.FRAME_NORMAL)
        self.items_frame.pack(fill=tk.BOTH, expand=True)

    def set_optimal_items(self, items: Optional[List[str]]):
        """Set the list of optimal items.
        
        Args:
            items: List of optimal item names, or None to clear
        """
        self.optimal_items = items or []
        self.refresh()

    def display_items(self, items: Dict[str, Item]):
        """Display the given items.
        
        Args:
            items: Dictionary of items to display
        """
        print(f"ItemList display_items called with {len(items)} items")
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        print("Cleared existing items")
        
        if not items:
            print("No items to display")
            return
            
        # Split items into optimal and regular
        optimal_items = {}
        regular_items = {}
        
        for name, item in items.items():
            if name in self.optimal_items:
                optimal_items[name] = item
            else:
                regular_items[name] = item
        
        print(f"Split into {len(optimal_items)} optimal and {len(regular_items)} regular items")
        
        # Sort optimal items by weight per 1000 price
        sorted_optimal = sorted(
            optimal_items.items(),
            key=lambda x: -x[1].weight_per_1k
        )
        
        # Sort regular items: None category first, then favorites, then rest
        sorted_regular = sorted(
            regular_items.items(),
            key=lambda x: (
                x[1].category != 'None',  # None category first
                not x[1].favorite,        # Then favorites
                -x[1].weight_per_1k      # Then by weight per price
            )
        )
        
        # Display optimal items in view mode
        if sorted_optimal:
            print("Displaying optimal items")
            self._display_view_mode(sorted_optimal)
            if sorted_regular:
                self._add_separator()
        # Display regular items in view mode
        if sorted_regular:
            print("Displaying regular items")
            self._display_view_mode(sorted_regular)
        
        print(f"Final items frame children: {self.items_frame.winfo_children()}")

    def _display_view_mode(self, items):
        """Display items in view mode - responsive grid layout.
        
        Args:
            items: List of (name, item) tuples to display
        """
        print(f"_display_view_mode called with {len(items)} items")
        # Create a frame to hold rows
        rows_frame = tk.Frame(self.items_frame, **Style.FRAME_NORMAL)
        rows_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns
        for i in range(self.current_columns):
            rows_frame.grid_columnconfigure(i, weight=1, uniform="col", 
                                         pad=UIConstant.CARD_PADDING)
        
        # Display items in a grid
        for i, (name, item) in enumerate(items):
            print(f"Creating card for item {name}")
            # Calculate grid position
            row = i // self.current_columns
            col = i % self.current_columns
            
            # Create item frame
            item_frame = tk.Frame(rows_frame, bd=1, relief=tk.GROOVE, 
                                width=UIConstant.CARD_WIDTH,
                                bg=Style.BG_DARKER)
            item_frame.grid(row=row, column=col, padx=UIConstant.CARD_PADDING, 
                          pady=UIConstant.CARD_PADDING, sticky="nsew")
            item_frame.grid_propagate(False)
            
            # Inner frame for content
            content_frame = tk.Frame(item_frame, **Style.FRAME_NORMAL)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)
            
            # Name Label (left) and Edit button (right)
            name_row = tk.Frame(content_frame, **Style.FRAME_NORMAL)
            name_row.pack(fill=tk.X)
            
            # Create a modified style without font
            label_style = {k: v for k, v in Style.LABEL_NORMAL.items() if k != 'font'}
            name_label = tk.Label(name_row, text=name, 
                                font=("Arial", 10, "bold"),
                                anchor="w", wraplength=UIConstant.CARD_WIDTH-48,
                                **label_style)
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Create a modified style without font
            btn_style = {k: v for k, v in Style.BTN_NORMAL.items() if k != 'font'}
            edit_button = tk.Button(name_row, text="Edit", width=7, height=1,
                                  command=lambda n=name: self.on_edit(n),
                                  font=("Arial", 9),
                                  **btn_style)
            edit_button.pack(side=tk.RIGHT, padx=(6, 0))
            
            # Stats frame
            stats_frame = tk.Frame(content_frame, **Style.FRAME_NORMAL)
            stats_frame.pack(fill=tk.X)
            tk.Label(stats_frame, text=f"P: {item.price}", 
                    anchor="w", **label_style).pack(side=tk.LEFT)
            tk.Label(stats_frame, text=f"A: {item.adjustment}", 
                    anchor="w", **label_style).pack(side=tk.LEFT, padx=(6, 0))
            tk.Label(stats_frame, text=f"W: {item.total_weight:.1f}", 
                    anchor="w", **label_style).pack(side=tk.LEFT, padx=(6, 0))
            
            # Weight per 1000 Price
            efficiency_frame = tk.Frame(content_frame, **Style.FRAME_NORMAL)
            efficiency_frame.pack(fill=tk.X)
            tk.Label(efficiency_frame, text=f"W/kP: {item.weight_per_1k:.1f}", 
                    anchor="w", **label_style).pack(side=tk.LEFT)
            
            # Category and Favorite status
            status_text = f"{item.category}"
            if item.favorite:
                status_text += " ★"
            tk.Label(content_frame, text=status_text, 
                    anchor="w", **label_style).pack(fill=tk.X)
            
            # Effects
            if item.effects.strip():
                tk.Label(content_frame, text=item.effects, anchor="w",
                        wraplength=UIConstant.CARD_WIDTH-12,
                        **label_style).pack(fill=tk.X, pady=(1, 2))
            
            # Optional fields
            optional_text = []
            for field, value in item.stats.items():
                if value > 0:
                    optional_text.append(f"{field}: {value}")
            if optional_text:
                tk.Label(content_frame, text=", ".join(optional_text),
                        anchor="w", wraplength=UIConstant.CARD_WIDTH-12,
                        **label_style).pack(fill=tk.X, pady=(0, 2))
        print(f"Finished creating {len(items)} cards")

    def _add_separator(self):
        """Add a separator line between sections."""
        separator = tk.Frame(self.items_frame, height=2, bd=1, relief=tk.SUNKEN,
                           bg=Style.BORDER)
        separator.pack(fill=tk.X, padx=5, pady=10)

    def refresh(self):
        """Refresh the current display."""
        # Call parent's refresh directly
        if self.parent_window and hasattr(self.parent_window, '_refresh_display'):
            self.parent_window._refresh_display()

    def update_columns(self, width: int):
        """Update the number of columns based on available width.
        
        Args:
            width: Available width in pixels
        """
        # Calculate how many columns can fit
        available_width = width - 20  # Reduced padding allowance
        columns = max(1, min(8, available_width // (UIConstant.CARD_WIDTH + 2 * UIConstant.CARD_PADDING)))
        
        if columns != self.current_columns:
            self.current_columns = columns
            self.refresh() 