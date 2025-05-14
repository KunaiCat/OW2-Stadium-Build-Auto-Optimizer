"""Item list component for displaying items in grid or list view."""
import tkinter as tk
from typing import Dict, Callable, List, Optional
from models.item import Item
from utils.constants import UIConstant

class ItemList(tk.Frame):
    """Component for displaying items in grid or list view."""

    def __init__(self, parent: tk.Widget, on_edit: Callable[[str], None]):
        """Initialize the item list.
        
        Args:
            parent: Parent widget
            on_edit: Callback for when an item is selected for editing
        """
        super().__init__(parent)
        self.on_edit = on_edit
        
        # Find parent window
        self.parent_window = parent
        while self.parent_window and not hasattr(self.parent_window, '_refresh_display'):
            self.parent_window = self.parent_window.master
        
        # Display state
        self.current_columns = UIConstant.DEFAULT_COLUMNS
        self.edit_mode = False
        self.optimal_items: List[str] = []
        
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Canvas for scrolling
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, 
                                    command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame to hold items
        self.items_frame = tk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), 
                                                    window=self.items_frame, 
                                                    anchor="nw")
        
        # Configure canvas
        self.items_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def set_edit_mode(self, enabled: bool):
        """Set whether edit mode is enabled.
        
        Args:
            enabled: True to enable edit mode
        """
        self.edit_mode = enabled
        # Call parent's refresh directly to update the display
        if self.parent_window and hasattr(self.parent_window, '_refresh_display'):
            self.parent_window._refresh_display()

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
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        if not items:
            return
            
        # Split items into optimal and regular
        optimal_items = {}
        regular_items = {}
        
        for name, item in items.items():
            if name in self.optimal_items:
                optimal_items[name] = item
            else:
                regular_items[name] = item
        
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
        
        # Display items based on mode
        if self.edit_mode:
            # Display optimal items in edit mode
            if sorted_optimal:
                self._display_edit_mode(sorted_optimal)
                if sorted_regular:
                    self._add_separator()
            # Display regular items in edit mode
            if sorted_regular:
                self._display_edit_mode(sorted_regular)
        else:
            # Display optimal items in view mode
            if sorted_optimal:
                self._display_view_mode(sorted_optimal)
                if sorted_regular:
                    self._add_separator()
            # Display regular items in view mode
            if sorted_regular:
                self._display_view_mode(sorted_regular)

    def _display_edit_mode(self, items):
        """Display items in edit mode - full width with edit controls.
        
        Args:
            items: List of (name, item) tuples to display
        """
        for name, item in items:
            # Create item frame
            item_frame = tk.Frame(self.items_frame, bd=1, relief=tk.GROOVE)
            item_frame.pack(fill=tk.X, pady=10, padx=5)
            
            # Name row with Edit button
            name_frame = tk.Frame(item_frame)
            name_frame.pack(fill=tk.X, pady=(5, 2), padx=10)
            
            # Name label on left
            name_label = tk.Label(name_frame, text=name, 
                                font=("Arial", 12, "bold"), anchor="w")
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Edit button on right
            edit_button = tk.Button(name_frame, text="Edit", width=10, height=1,
                                  command=lambda n=name: self.on_edit(n),
                                  font=("Arial", 10))
            edit_button.pack(side=tk.RIGHT, padx=(10, 0))
            
            # Stats row
            stats_frame = tk.Frame(item_frame)
            stats_frame.pack(fill=tk.X, pady=2, padx=10)
            
            stats_text = (f"Price: {item.price}   |   "
                         f"Adjustment: {item.adjustment}   |   "
                         f"Effect Value: {item.effect_value}   |   "
                         f"Total Weight: {item.total_weight:.1f} "
                         f"(W/kP: {item.weight_per_1k:.1f})")
            
            stats_label = tk.Label(stats_frame, text=stats_text, anchor="w")
            stats_label.pack(fill=tk.X)
            
            # Status row
            status_frame = tk.Frame(item_frame)
            status_frame.pack(fill=tk.X, pady=2, padx=10)
            
            status_text = (f"Category: {item.category}   |   "
                         f"Favorite: {'Yes' if item.favorite else 'No'}")
            
            status_label = tk.Label(status_frame, text=status_text, anchor="w")
            status_label.pack(fill=tk.X)
            
            # Effects row
            if item.effects.strip():
                effects_frame = tk.Frame(item_frame)
                effects_frame.pack(fill=tk.X, pady=2, padx=10)
                effects_label = tk.Label(effects_frame, 
                                       text=f"Effects: {item.effects}",
                                       anchor="w", wraplength=800)
                effects_label.pack(fill=tk.X)
            
            # Optional fields row
            optional_fields = []
            for field, value in item.stats.items():
                if value > 0:
                    optional_fields.append(f"{field}: {value}")
            
            if optional_fields:
                optional_frame = tk.Frame(item_frame)
                optional_frame.pack(fill=tk.X, pady=2, padx=10)
                optional_text = "   |   ".join(optional_fields)
                optional_label = tk.Label(optional_frame, text=optional_text, 
                                        anchor="w")
                optional_label.pack(fill=tk.X)

    def _display_view_mode(self, items):
        """Display items in view mode - responsive grid layout.
        
        Args:
            items: List of (name, item) tuples to display
        """
        # Create a frame to hold rows
        rows_frame = tk.Frame(self.items_frame)
        rows_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns
        for i in range(self.current_columns):
            rows_frame.grid_columnconfigure(i, weight=1, uniform="col", 
                                         pad=UIConstant.CARD_PADDING)
        
        # Display items in a grid
        for i, (name, item) in enumerate(items):
            # Calculate grid position
            row = i // self.current_columns
            col = i % self.current_columns
            
            # Create item frame
            item_frame = tk.Frame(rows_frame, bd=1, relief=tk.GROOVE, 
                                width=UIConstant.CARD_WIDTH)
            item_frame.grid(row=row, column=col, padx=UIConstant.CARD_PADDING, 
                          pady=UIConstant.CARD_PADDING, sticky="nsew")
            item_frame.grid_propagate(False)
            
            # Inner frame for content
            content_frame = tk.Frame(item_frame)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)
            
            # Name Label
            name_label = tk.Label(content_frame, text=name, 
                                font=("Arial", 10, "bold"),
                                anchor="w", wraplength=UIConstant.CARD_WIDTH-12)
            name_label.pack(fill=tk.X, pady=(2, 1))
            
            # Stats frame
            stats_frame = tk.Frame(content_frame)
            stats_frame.pack(fill=tk.X)
            tk.Label(stats_frame, text=f"P: {item.price}", 
                    anchor="w").pack(side=tk.LEFT)
            tk.Label(stats_frame, text=f"A: {item.adjustment}", 
                    anchor="w").pack(side=tk.LEFT, padx=(6, 0))
            tk.Label(stats_frame, text=f"W: {item.total_weight:.1f}", 
                    anchor="w").pack(side=tk.LEFT, padx=(6, 0))
            
            # Weight per 1000 Price
            efficiency_frame = tk.Frame(content_frame)
            efficiency_frame.pack(fill=tk.X)
            tk.Label(efficiency_frame, text=f"W/kP: {item.weight_per_1k:.1f}", 
                    anchor="w").pack(side=tk.LEFT)
            
            # Category and Favorite status
            status_text = f"{item.category}"
            if item.favorite:
                status_text += " ★"
            tk.Label(content_frame, text=status_text, 
                    anchor="w").pack(fill=tk.X)
            
            # Effects
            if item.effects.strip():
                tk.Label(content_frame, text=item.effects, anchor="w",
                        wraplength=UIConstant.CARD_WIDTH-12).pack(fill=tk.X, pady=(1, 2))
            
            # Optional fields
            optional_text = []
            for field, value in item.stats.items():
                if value > 0:
                    optional_text.append(f"{field}: {value}")
            if optional_text:
                tk.Label(content_frame, text=", ".join(optional_text),
                        anchor="w", wraplength=UIConstant.CARD_WIDTH-12).pack(fill=tk.X, 
                                                                 pady=(0, 2))

    def _add_separator(self):
        """Add a separator line between sections."""
        separator = tk.Frame(self.items_frame, height=2, bd=1, relief=tk.SUNKEN)
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

    def _on_frame_configure(self, event):
        """Update the scroll region to encompass the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Resize the inner frame to match the canvas."""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units") 