"""Item editor component for creating and editing items."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Callable, Optional
from models.item import Item
from models.category import Category
from utils.constants import OptionalField
from utils.validators import validate_item_input

class ItemEditor(tk.Frame):
    """Component for editing item details."""

    def __init__(self, parent: tk.Widget,
                 on_save: Callable[[str, Item], bool],
                 on_delete: Callable[[str], bool],
                 on_cancel: Callable[[], None]):
        """Initialize the item editor.
        
        Args:
            parent: Parent widget
            on_save: Callback for saving changes
            on_delete: Callback for deleting items
            on_cancel: Callback for canceling edit
        """
        super().__init__(parent)
        self.on_save = on_save
        self.on_delete = on_delete
        self.on_cancel = on_cancel
        
        # Current item being edited
        self.current_item: Optional[str] = None
        
        # UI state
        self.optional_entries: Dict[str, Dict] = {}
        
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Top row: Name, Category radios, and Favorite
        top_row = tk.Frame(self)
        top_row.pack(fill=tk.X, pady=(0, 5))
        
        # Name label and entry
        tk.Label(top_row, text="Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_entry = tk.Entry(top_row, width=30)
        self.name_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Category radio buttons with labels
        self.category_var = tk.StringVar(value=Category.NONE)
        categories = [
            ("W", Category.WEAPON),
            ("A", Category.ABILITY),
            ("S", Category.SURVIVAL)
        ]
        for label, value in categories:
            rb = tk.Radiobutton(top_row, text=label, value=value, 
                              variable=self.category_var)
            rb.pack(side=tk.LEFT, padx=2)
        
        # Favorite checkbox
        self.favorite_var = tk.BooleanVar(value=False)
        favorite_check = tk.Checkbutton(top_row, text="★", 
                                      variable=self.favorite_var)
        favorite_check.pack(side=tk.RIGHT)
        
        # Middle section: Stats and Effects
        middle_frame = tk.Frame(self)
        middle_frame.pack(fill=tk.X, pady=5)
        
        # Left side - Stats
        stats_frame = tk.Frame(middle_frame)
        stats_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Stats entries
        self.stats_entries = {}
        stats = [
            ("Price", ""),
            ("Adjustment", "0"),
            ("Effect Value", "0")
        ]
        
        for label, default in stats:
            row = tk.Frame(stats_frame)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{label}:").pack(side=tk.LEFT, padx=(0, 5))
            entry = tk.Entry(row, width=10)
            entry.insert(0, default)
            entry.pack(side=tk.LEFT)
            self.stats_entries[label.lower().replace(" ", "_")] = entry
        
        # Right side - Effects
        effects_frame = tk.Frame(middle_frame)
        effects_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        tk.Label(effects_frame, text="Effects:").pack(anchor="w")
        self.effects_text = tk.Text(effects_frame, height=3, width=40)
        self.effects_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom section: Optional fields and buttons
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Optional fields dropdown and add button
        options_frame = tk.Frame(bottom_frame)
        options_frame.pack(side=tk.LEFT)
        
        self.optional_dropdown = ttk.Combobox(options_frame, values=[f.value for f in OptionalField],
                                            state="readonly", width=20)
        self.optional_dropdown.set("Add field...")
        self.optional_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        
        add_field_button = tk.Button(options_frame, text="+", width=3,
                                   command=self._add_optional_field)
        add_field_button.pack(side=tk.LEFT)
        
        # Optional fields section
        self.optional_fields_frame = tk.Frame(self)
        self.optional_fields_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons frame
        buttons_frame = tk.Frame(bottom_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        # Delete button on left
        self.delete_button = tk.Button(buttons_frame, text="Delete", width=8,
                                     command=self._delete_item, fg="red")
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel and Confirm buttons
        self.confirm_button = tk.Button(buttons_frame, text="Confirm", width=8,
                                      command=self._confirm_edit)
        self.confirm_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = tk.Button(buttons_frame, text="Cancel", width=8,
                                command=self.on_cancel)
        cancel_button.pack(side=tk.RIGHT)

    def edit_item(self, name: str, item: Item):
        """Start editing an existing item.
        
        Args:
            name: Name of the item
            item: Item to edit
        """
        self.current_item = name
        
        # Set basic fields
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)
        self.category_var.set(item.category)
        self.favorite_var.set(item.favorite)
        
        # Set stats
        self.stats_entries["price"].delete(0, tk.END)
        self.stats_entries["price"].insert(0, str(item.price))
        
        self.stats_entries["adjustment"].delete(0, tk.END)
        self.stats_entries["adjustment"].insert(0, str(item.adjustment))
        
        self.stats_entries["effect_value"].delete(0, tk.END)
        self.stats_entries["effect_value"].insert(0, str(item.effect_value))
        
        # Set effects
        self.effects_text.delete("1.0", tk.END)
        self.effects_text.insert("1.0", item.effects)
        
        # Clear existing optional fields
        for widgets in self.optional_fields_frame.winfo_children():
            widgets.destroy()
        self.optional_entries.clear()
        
        # Add existing optional fields
        for field, value in item.stats.items():
            if value > 0:
                self._create_optional_field_entry(field, value)
        
        # Show delete button for existing items
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Focus name entry
        self.name_entry.focus_set()

    def new_item(self):
        """Start creating a new item."""
        self.current_item = None
        
        # Clear all fields
        self.name_entry.delete(0, tk.END)
        self.category_var.set(Category.NONE)
        self.favorite_var.set(False)
        
        for entry in self.stats_entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        
        self.effects_text.delete("1.0", tk.END)
        
        # Clear optional fields
        for widgets in self.optional_fields_frame.winfo_children():
            widgets.destroy()
        self.optional_entries.clear()
        
        # Hide delete button for new items
        self.delete_button.pack_forget()
        
        # Focus name entry
        self.name_entry.focus_set()

    def _create_optional_field_entry(self, field_name: str, value: int = 0):
        """Create an entry for an optional field.
        
        Args:
            field_name: Name of the field
            value: Initial value
        """
        frame = tk.Frame(self.optional_fields_frame)
        frame.pack(fill=tk.X, pady=1)
        
        # Label on left
        tk.Label(frame, text=f"{field_name}:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Entry in middle
        entry = tk.Entry(frame, width=10)
        entry.insert(0, str(value))
        entry.pack(side=tk.LEFT)
        
        # Remove button on right
        def remove_field():
            frame.destroy()
            if field_name in self.optional_entries:
                del self.optional_entries[field_name]
        
        remove_btn = tk.Button(frame, text="×", width=2, command=remove_field)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Store the widgets
        self.optional_entries[field_name] = {"frame": frame, "entry": entry}

    def _add_optional_field(self):
        """Add a new optional field."""
        field_name = self.optional_dropdown.get()
        if field_name == "Add field..." or field_name == "Select field to add":
            return
        
        # Check if field already exists
        if field_name in self.optional_entries:
            return
        
        # Create the new field entry
        self._create_optional_field_entry(field_name, 0)

    def _confirm_edit(self):
        """Confirm the current edit."""
        # Get the values
        name = self.name_entry.get()
        price = self.stats_entries["price"].get()
        adjustment = self.stats_entries["adjustment"].get()
        effect_value = self.stats_entries["effect_value"].get()
        
        # Validate input
        valid, error = validate_item_input(name, price, adjustment, effect_value)
        if not valid:
            messagebox.showerror("Validation Error", error)
            return
        
        # Create item data
        item = Item(
            name=name,
            price=int(price),
            adjustment=int(adjustment),
            effect_value=int(effect_value),
            effects=self.effects_text.get("1.0", tk.END).strip(),
            favorite=self.favorite_var.get(),
            category=Category(self.category_var.get() or Category.NONE)
        )
        
        # Add optional fields
        for field, widgets in self.optional_entries.items():
            try:
                value = int(widgets["entry"].get())
                if value > 0:
                    item.stats[field] = value
            except ValueError:
                messagebox.showerror("Validation Error",
                                   f"Invalid value for {field}. Must be a positive integer.")
                return
        
        # Save the item
        if self.on_save(self.current_item or name, item):
            self.on_cancel()
        else:
            messagebox.showerror("Error", "Failed to save item")

    def _delete_item(self):
        """Delete the current item."""
        if not self.current_item:
            return
            
        if messagebox.askyesno("Confirm Delete",
                              f"Are you sure you want to delete {self.current_item}?",
                              icon='warning'):
            if self.on_delete(self.current_item):
                self.on_cancel()
            else:
                messagebox.showerror("Error", "Failed to delete item") 