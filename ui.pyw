import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # For the Combobox
import json
import os
from enum import Enum
import math
class Category(str, Enum):
    WEAPON = "Weapon"
    ABILITY = "Ability"
    SURVIVAL = "Survival"
    NONE = "None"

OPTIONAL_FIELDS = ['Weapon Power', 'Weapon Lifesteal', 'Attack Speed', 
                  'Reload Speed', 'Move Speed', 'Critical Damage', 
                  'Melee Damage', 'Max Ammo', 'Cooldown Reduction', 
                  'Ability Power', 'Ability Lifesteal', 'Armor',
                  'Shields', 'Health']
REQUIRED_FIELDS = ['Price', 'Adjustment', 'Effect Value', 'Effects', 'Favorite', 'Category']

class ItemManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Item Manager")
        # Set initial window size
        self.root.geometry("1024x800")
        self.root.minsize(350, 600)  # Minimum size to fit one card plus padding
        self.root.resizable(True, True)
        
        # Card width constants
        self.CARD_WIDTH = 280  # Reduced from 300 to 280
        self.CARD_PADDING = 4  # Padding between cards
        self.current_columns = 3  # Default number of columns
        
        # Calculate exact window width needed for 3 columns
        # Formula: (card_width + 2*padding) * num_columns + 2*main_frame_padding + sidebar_width + sidebar_padding
        sidebar_width = 200  # Approximate width of sidebar
        main_frame_padding = 4  # Padding of main frame
        window_width = (self.CARD_WIDTH + 2*self.CARD_PADDING) * 3 + 2*main_frame_padding + sidebar_width + 4
        
        # Set initial window size
        self.root.geometry(f"{window_width}x800")
        self.root.minsize(350, 600)  # Minimum size to fit one card plus padding
        self.root.resizable(True, True)
        
        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
        # File path for items.json
        self.items_file = "items.json"
        
        # Variables for increment tracking
        self.increment = 1.0
        self.last_field = None
        
        # Category filter variables
        self.show_weapon = tk.BooleanVar(value=True)
        self.show_ability = tk.BooleanVar(value=True)
        self.show_survival = tk.BooleanVar(value=True)
        
        # Edit mode variable
        self.edit_mode = tk.BooleanVar(value=False)
        
        # Optimization mode - when True, shows only optimal items
        self.showing_optimal = False
        self.optimal_items = []
        
        # Main container
        self.container = tk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Top bar frame for edit mode toggle
        top_bar = tk.Frame(self.container)
        top_bar.pack(fill=tk.X, padx=2, pady=1)
        
        # Edit mode toggle in top left
        tk.Checkbutton(top_bar, text="Edit Mode", variable=self.edit_mode,
                      command=self.display_items).pack(side=tk.LEFT)
        
        # Hide weights toggle in top right
        self.hide_weights = tk.BooleanVar(value=False)
        tk.Checkbutton(top_bar, text="Hide Weights", variable=self.hide_weights,
                      command=self.toggle_sidebar).pack(side=tk.RIGHT)
        
        # Main content area (now on left)
        self.main_frame = tk.Frame(self.container)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Sidebar for weights (now on right)
        self.sidebar = tk.Frame(self.container, bd=1, relief=tk.SOLID)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
        
        # Initialize weights dictionary
        self.weights = {}
        self.weight_vars = {}  # To store StringVar for each weight
        
        # Setup sidebar
        self.setup_sidebar()
        
        # Search frame at top
        search_frame = tk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search label
        tk.Label(search_frame, text="Search/Enter Budget:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Bind the Enter key to trigger find_optimal_items
        self.search_entry.bind("<Return>", lambda event: self.check_and_find_optimal_items())
        
        # Find Best Items button (hidden by default)
        self.find_best_button = tk.Button(search_frame, text="Find Best Items", 
                                        command=self.find_optimal_items)
        
        # Reset button (hidden by default)
        self.reset_button = tk.Button(search_frame, text="Reset", 
                                    command=self.reset_view)
        
        # Category filter frame
        filter_frame = tk.Frame(self.main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Category filter label
        tk.Label(filter_frame, text="Show Categories:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Category checkboxes
        tk.Checkbutton(filter_frame, text="Weapon", variable=self.show_weapon,
                      command=self.display_items).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(filter_frame, text="Ability", variable=self.show_ability,
                      command=self.display_items).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(filter_frame, text="Survival", variable=self.show_survival,
                      command=self.display_items).pack(side=tk.LEFT, padx=5)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame to hold item list
        self.items_frame = tk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.items_frame, anchor="nw")
        
        # Title
        title_label = tk.Label(self.items_frame, text="Item Manager", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # List frame
        self.list_frame = tk.Frame(self.items_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # New item frame
        self.setup_new_item_frame()
        
        # Load data
        self.load_items()
        self.display_items()
        
        # Track application focus state
        self.app_has_focus = False
        # Bind focus events to handle initial window focus
        self.root.bind("<FocusIn>", self.on_window_focus_in)
        self.root.bind("<FocusOut>", self.on_window_focus_out)

    def on_window_focus_in(self, event):
        """Handle window receiving focus"""
        # Only focus the search entry if the application was previously unfocused
        if not self.app_has_focus and event.widget == self.root:
            self.search_entry.focus_set()
        self.app_has_focus = True
    
    def on_window_focus_out(self, event):
        """Track when application loses focus"""
        if event.widget == self.root:
            self.app_has_focus = False

    def round_to_nearest_fraction(self, value):
        """Round a number to the nearest third, quarter, or tenth"""
        # First round to 2 decimal places
        value = round(value, 2)
        
        # Find the nearest third (0.33, 0.67, 1.00, 1.33, etc)
        thirds = round(value * 3) / 3
        
        # Find the nearest quarter (0.25, 0.50, 0.75, 1.00, etc)
        quarters = round(value * 4) / 4
        
        # Find the nearest tenth (0.1, 0.2, 0.3, etc)
        scores = round(value * 20) / 20
        
        # Find which one is closest to the original value
        options = [thirds, quarters, scores]
        differences = [abs(value - opt) for opt in options]
        closest = options[differences.index(min(differences))]
        
        return round(closest, 2)

    def adjust_weight(self, field, is_increment):
        """Adjusts a weight value using a dynamic increment system.
        
        The increment value is determined by how many times the user has pressed the same button in sequence.
        The system tracks a 'repeats' counter that ranges from -10 to +10, which maps to predefined increment values.
        
        Args:
            field (str): The weight field to adjust (e.g., 'Adjustment', 'Effect Value', etc.)
            is_increment (bool): True for increment (+), False for decrement (-)
        
        The increment selection works as follows:
        - First press starts at ±1.0
        - Consecutive same-direction presses increase the magnitude
        - Switching directions reduces the magnitude
        - Switching fields resets the system
        """
        try:
            # Handle field switching - reset state when user switches to a different field
            if field != self.last_field:
                self.untouched = True
                self.last_field = field

            current = float(self.weight_vars[field].get())

            # Update repeats counter based on button press pattern
            if self.untouched:
                # First press for this field
                self.repeats = -2
                self.untouched = False
            elif is_increment == self.last_increment:
                # Consecutive press in same direction
                self.repeats += 1
            else:
                # Changed direction - reduce magnitude
                self.repeats -= 2

            # Clamp repeats to valid range
            self.repeats = max(min(self.repeats, 15), -15)
            
            # Map repeats counter to increment value
            # Index calculation: (-15 to +15) -> (0 to 10)
            index_from_repeats = int((self.repeats + 15) / 2)
            
            # Predefined increment values in ascending order
            possible_increments = [0.05, 0.1, 0.2, 0.33, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 8.0]
            
            # Select and apply increment
            increment = possible_increments[index_from_repeats]
            if not is_increment:
                increment *= -1
                
            new_value = current + increment

            # Round the result appropriately
            new_value = round(new_value, 2)
            new_value = self.round_to_nearest_fraction(new_value)

            # Store state for next press
            self.last_increment = is_increment

            # Update UI and save
            self.weight_vars[field].set(f"{new_value:.2f}")
            self.weights[field] = new_value
            self.save_items()
            
        except ValueError:
            messagebox.showerror("Error", f"Invalid weight value for {field}")

    def on_weight_change(self, field, *args):
        """Handle manual changes to weight values.
        
        Called when the user types or modifies a weight value directly in the entry field.
        Validates the input and updates the stored weight if valid.
        """
        try:
            # Get the new value from the StringVar
            new_value = float(self.weight_vars[field].get())
            
            # Round and normalize the value
            new_value = round(new_value, 2)
            new_value = self.round_to_nearest_fraction(new_value)
            
            # Update the display with the normalized value
            self.weight_vars[field].set(f"{new_value:.2f}")
            
            # Update stored weight and save
            self.weights[field] = new_value
            self.save_items()
        except ValueError:
            # Ignore invalid input - let the user continue typing
            pass

    def load_items(self):
        """Load items and weights from JSON file"""
        try:
            if os.path.exists(self.items_file):
                with open(self.items_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'items' in data and 'weights' in data:
                        # New format
                        self.items = data['items']
                        self.weights = data['weights']
                    else:
                        # Old format - migrate
                        self.items = data
                        self.weights = self.create_default_weights()
            else:
                self.items = {}
                self.weights = self.create_default_weights()
                self.save_items()
            
            # Calculate total weights for all items
            self.calculate_total_weights()
            
            # Update weight vars
            for field, weight in self.weights.items():
                if field in self.weight_vars:
                    self.weight_vars[field].set(f"{weight:.2f}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items: {str(e)}")
            self.items = {}
            self.weights = self.create_default_weights()

    def create_default_weights(self):
        """Create default weights dictionary"""
        weights = {'Adjustment': 1.0, 'Effect Value': 1.0}
        for field in OPTIONAL_FIELDS:
            weights[field] = 1.0
        return weights

    def calculate_total_weights(self):
        """Calculate and save Total Weight for each item based on weights dictionary.
        
        Total Weight is calculated by:
        1. Finding all fields in the item that exist in the weights dictionary
        2. Multiplying each field's value by its corresponding weight
        3. Summing all the weighted values
        4. Saving the total as 'Total Weight' in the item's stats
        """
        # Loop through all items
        for item_name, item_data in self.items.items():
            total_weight = 0
            
            # Check each field in the item against the weights dictionary
            for field, weight in self.weights.items():
                if field in item_data:
                    # Multiply the item's value by the weight and add to total
                    total_weight += item_data[field] * weight
            
            # Save the Total Weight back to the item
            item_data['Total Weight'] = round(total_weight, 2)

    def save_items(self):
        """Save items and weights to JSON file"""
        try:
            # Update weights from StringVars
            for field, var in self.weight_vars.items():
                try:
                    self.weights[field] = float(var.get())
                except ValueError:
                    self.weights[field] = 1.0
                    var.set("1.00")
            
            # Calculate total weights before saving
            self.calculate_total_weights()
            
            # Save both items and weights
            data = {
                'items': self.items,
                'weights': self.weights
            }
            with open(self.items_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save items: {str(e)}")

    def on_frame_configure(self, event):
        """Update the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Resize the inner frame to match the canvas"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def validate_input(self, name, price, adjustment, effect_value):
        """Validate input values"""
        if not name.strip():
            messagebox.showerror("Validation Error", "Name is required")
            return False
        
        try:
            price_val = int(price)
            if price_val <= 0:
                messagebox.showerror("Validation Error", "Price must be a positive integer")
                return False
        except ValueError:
            messagebox.showerror("Validation Error", "Price must be a valid integer")
            return False
        
        try:
            adjustment_val = int(adjustment)
            if adjustment_val < 0:
                messagebox.showerror("Validation Error", "Adjustment must be a non-negative integer")
                return False
        except ValueError:
            messagebox.showerror("Validation Error", "Adjustment must be a valid integer")
            return False

        try:
            effect_value_val = int(effect_value)
            if effect_value_val < 0:
                messagebox.showerror("Validation Error", "Effect Value must be a non-negative integer")
                return False
        except ValueError:
            messagebox.showerror("Validation Error", "Effect Value must be a valid integer")
            return False
        
        return True
    
    def clear_list_frame(self):
        """Clear all widgets from the list frame"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
    
    def on_search_change(self, *args):
        """Called when the search text changes"""
        search_text = self.search_var.get().strip()
        
        # Check if the search text is a valid budget
        try:
            value = int(search_text)
            if value >= 3500:
                # Show Find Best Items button
                self.find_best_button.pack(side=tk.RIGHT, padx=5)
            else:
                # Hide Find Best Items button
                self.find_best_button.pack_forget()
        except ValueError:
            # Not a valid integer, hide Find Best Items button
            self.find_best_button.pack_forget()
        
        # Show Reset button if we have optimal items
        if self.optimal_items:
            self.reset_button.pack(side=tk.RIGHT, padx=5)
        else:
            self.reset_button.pack_forget()
        
        # Update display
        self.display_items()
    
    def display_items(self):
        """Display all items in the list frame"""
        self.clear_list_frame()
        
        # Get search text and convert to lowercase
        search_text = self.search_var.get().strip().lower()
        
        # Check if search text is purely numeric
        is_numeric = search_text.isdigit()
        
        # First, get optimal items if they exist
        optimal_filtered = {}
        if self.optimal_items:
            for name in self.optimal_items:
                if name in self.items:
                    # Include optimal items regardless of search or category filters
                    optimal_filtered[name] = self.items[name]
        
        # Then get regular filtered items
        filtered_items = {}
        # Always include regular items, even in optimization view
        for name, details in self.items.items():
            # Skip if already in optimal items
            if name in optimal_filtered:
                continue
                
            # Skip if doesn't match search text (only if search text is non-numeric)
            if not is_numeric and search_text and search_text not in name.strip().lower():
                continue
                
            # Always show items with Category "None"
            category = details.get('Category', 'None')
            if category == 'None':
                filtered_items[name] = details
                continue
                
            # Apply category filters
            if (category == 'Weapon' and self.show_weapon.get() or
                category == 'Ability' and self.show_ability.get() or
                category == 'Survival' and self.show_survival.get()):
                filtered_items[name] = details
        
        # Calculate Weight per 1000 Price for all items
        for items_dict in [optimal_filtered, filtered_items]:
            for name, details in items_dict.items():
                total_weight = details.get('Total Weight', 0)
                weight_per_1k = (total_weight * 1000) / details['Price']
                details['weight_per_1k'] = weight_per_1k
        
        # Sort optimal items by Weight per 1000 Price
        sorted_optimal = sorted(
            optimal_filtered.items(),
            key=lambda x: -x[1].get('weight_per_1k', 0)  # Sort by Weight per 1000 Price (descending)
        )
        
        # Sort regular items: None category first, then favorites, then rest
        sorted_regular = sorted(
            filtered_items.items(),
            key=lambda x: (
                x[1].get('Category', 'None') != 'None',  # None category first
                not x[1].get('Favorite', False),         # Then favorites
                -x[1].get('weight_per_1k', 0)           # Then by Weight per 1000 Price (descending)
            )
        )
        
        if self.edit_mode.get():
            # Display optimal items
            if sorted_optimal:
                self._display_edit_mode(sorted_optimal)
                # Add separator if there are regular items to show
                if sorted_regular:
                    separator = tk.Frame(self.list_frame, height=2, bd=1, relief=tk.SUNKEN)
                    separator.pack(fill=tk.X, padx=5, pady=10)
            # Display regular items
            if sorted_regular:
                self._display_edit_mode(sorted_regular)
            self.new_item_frame.pack(fill=tk.X, padx=5, pady=10)
        else:
            # Display optimal items
            if sorted_optimal:
                self._display_view_mode(sorted_optimal)
                # Add separator if there are regular items to show
                if sorted_regular:
                    separator = tk.Frame(self.list_frame, height=2, bd=1, relief=tk.SUNKEN)
                    separator.pack(fill=tk.X, padx=5, pady=10)
            # Display regular items
            if sorted_regular:
                self._display_view_mode(sorted_regular)
            self.new_item_frame.pack_forget()
    
    def _display_edit_mode(self, sorted_items):
        """Display items in edit mode - full width with edit controls"""
        for name, details in sorted_items:
            # Create a frame for the item with padding and border
            item_frame = tk.Frame(self.list_frame, bd=1, relief=tk.GROOVE)
            item_frame.pack(fill=tk.X, pady=10, padx=5)
            
            # Store item data and widgets
            item_data = {
                "name": name,
                "Price": details["Price"],
                "Adjustment": details["Adjustment"],
                "Effect Value": details.get("Effect Value", 0),
                "Effects": details.get("Effects", ""),
                "Favorite": details.get("Favorite", False),
                "Category": details.get("Category", Category.NONE),
                "widgets": {}
            }
            
            # Name row with Edit button
            name_frame = tk.Frame(item_frame)
            name_frame.pack(fill=tk.X, pady=(5, 2), padx=10)
            
            # Name label on left
            name_label = tk.Label(name_frame, text=name, font=("Arial", 12, "bold"), anchor="w")
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            item_data["widgets"]["name"] = name_label
            
            # Edit button on right
            edit_button = tk.Button(name_frame, text="Edit", width=10, height=1,
                                  command=lambda n=name: self.edit_item(n),
                                  font=("Arial", 10))
            edit_button.pack(side=tk.RIGHT, padx=(10, 0))
            item_data["widgets"]["edit_button"] = edit_button
            
            # Stats row (Price, Adjustment, Effect Value, Total Weight)
            stats_frame = tk.Frame(item_frame)
            stats_frame.pack(fill=tk.X, pady=2, padx=10)
            
            # Calculate stats
            total_weight = details.get('Total Weight', 0)
            weight_per_1k = (total_weight * 1000) / details['Price']
            
            # Create stats text with separators
            stats_text = f"Price: {details['Price']}   |   Adjustment: {details['Adjustment']}   |   "
            stats_text += f"Effect Value: {details.get('Effect Value', 0)}   |   "
            stats_text += f"Total Weight: {total_weight:.1f} (W/kP: {weight_per_1k:.1f})"
            
            stats_label = tk.Label(stats_frame, text=stats_text, anchor="w")
            stats_label.pack(fill=tk.X)
            
            # Status row (Category, Favorite)
            status_frame = tk.Frame(item_frame)
            status_frame.pack(fill=tk.X, pady=2, padx=10)
            
            category = details.get('Category', Category.NONE)
            favorite = details.get('Favorite', False)
            status_text = f"Category: {category}   |   Favorite: {'Yes' if favorite else 'No'}"
            
            status_label = tk.Label(status_frame, text=status_text, anchor="w")
            status_label.pack(fill=tk.X)
            
            # Effects row (if any)
            if details.get('Effects', '').strip():
                effects_frame = tk.Frame(item_frame)
                effects_frame.pack(fill=tk.X, pady=2, padx=10)
                effects_label = tk.Label(effects_frame, text=f"Effects: {details['Effects']}", 
                                       anchor="w", wraplength=800)
                effects_label.pack(fill=tk.X)
            
            # Optional fields row
            optional_fields = []
            for field in OPTIONAL_FIELDS:
                if field in details and details[field] > 0:
                    optional_fields.append(f"{field}: {details[field]}")
            
            if optional_fields:
                optional_frame = tk.Frame(item_frame)
                optional_frame.pack(fill=tk.X, pady=2, padx=10)
                optional_text = "   |   ".join(optional_fields)
                optional_label = tk.Label(optional_frame, text=optional_text, anchor="w")
                optional_label.pack(fill=tk.X)
            
            # Store the item data for future reference
            item_frame.item_data = item_data

    def _display_view_mode(self, sorted_items):
        """Display items in view mode - responsive grid layout"""
        # Create a frame to hold rows
        rows_frame = tk.Frame(self.list_frame)
        rows_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid columns
        for i in range(self.current_columns):
            rows_frame.grid_columnconfigure(i, weight=1, uniform="col", pad=self.CARD_PADDING)
        
        # Display items in a grid
        for i, (name, details) in enumerate(sorted_items):
            # Calculate grid position
            row = i // self.current_columns
            col = i % self.current_columns
            
            # Create compact item frame with fixed width
            item_frame = tk.Frame(rows_frame, bd=1, relief=tk.GROOVE, width=self.CARD_WIDTH)
            item_frame.grid(row=row, column=col, padx=self.CARD_PADDING, pady=self.CARD_PADDING, sticky="nsew")
            item_frame.grid_propagate(False)  # Prevent frame from shrinking
            
            # Inner frame for content
            content_frame = tk.Frame(item_frame)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)
            
            # Name Label (larger font)
            name_label = tk.Label(content_frame, text=name, font=("Arial", 10, "bold"), 
                                anchor="w", wraplength=self.CARD_WIDTH-12)
            name_label.pack(fill=tk.X, pady=(2, 1))
            
            # Price, Adjustment, and Total Weight on same line
            stats_frame = tk.Frame(content_frame)
            stats_frame.pack(fill=tk.X)
            tk.Label(stats_frame, text=f"P: {details['Price']}", anchor="w").pack(side=tk.LEFT)
            tk.Label(stats_frame, text=f"A: {details['Adjustment']}", anchor="w").pack(side=tk.LEFT, padx=(6, 0))
            
            # Total Weight and Weight per 1000 Price
            total_weight = details.get('Total Weight', 0)
            weight_per_1k = (total_weight * 1000) / details['Price']
            tk.Label(stats_frame, text=f"W: {total_weight:.1f}", anchor="w").pack(side=tk.LEFT, padx=(6, 0))
            
            # Weight per 1000 Price on new line
            efficiency_frame = tk.Frame(content_frame)
            efficiency_frame.pack(fill=tk.X)
            tk.Label(efficiency_frame, text=f"W/kP: {weight_per_1k:.1f}", anchor="w").pack(side=tk.LEFT)
            
            # Category and Favorite status (if applicable)
            category = details.get('Category', 'None')
            favorite = details.get('Favorite', False)
            status_text = f"{category}"
            if favorite:
                status_text += " ★"  # Star for favorites
            tk.Label(content_frame, text=status_text, anchor="w").pack(fill=tk.X)
            
            # Effects (if any)
            effects_text = details.get('Effects', '').strip()
            if effects_text:
                tk.Label(content_frame, text=effects_text, anchor="w", 
                        wraplength=self.CARD_WIDTH-12).pack(fill=tk.X, pady=(1, 2))
            
            # Optional fields (compact display)
            optional_text = []
            for field in OPTIONAL_FIELDS:
                if field in details and details[field] > 0:
                    optional_text.append(f"{field}: {details[field]}")
            if optional_text:
                tk.Label(content_frame, text=", ".join(optional_text), 
                        anchor="w", wraplength=self.CARD_WIDTH-12).pack(fill=tk.X, pady=(0, 2))

    def edit_item(self, name):
        """Edit an item with a horizontal layout"""
        # Find the item frame
        for item_frame in self.list_frame.winfo_children():
            if hasattr(item_frame, "item_data") and item_frame.item_data["name"] == name:
                item_data = item_frame.item_data
                
                # Hide all labels
                for widget_name, widget in item_data["widgets"].items():
                    if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                        widget.pack_forget()
                
                # Main edit frame
                edit_frame = tk.Frame(item_frame)
                edit_frame.pack(fill=tk.X, padx=10, pady=5)
                
                # Top row: Name, Category radios, and Favorite
                top_row = tk.Frame(edit_frame)
                top_row.pack(fill=tk.X, pady=(0, 5))
                
                # Name label and entry
                tk.Label(top_row, text="Name:").pack(side=tk.LEFT, padx=(0, 5))
                name_entry = tk.Entry(top_row, width=30)
                name_entry.insert(0, name)
                name_entry.pack(side=tk.LEFT, padx=(0, 10))
                
                # Category radio buttons with labels
                category_var = tk.StringVar(value=self.items[name].get("Category", Category.NONE))
                categories = [
                    ("W", Category.WEAPON),
                    ("A", Category.ABILITY),
                    ("S", Category.SURVIVAL)
                ]
                for label, value in categories:
                    rb = tk.Radiobutton(top_row, text=label, value=value, variable=category_var)
                    rb.pack(side=tk.LEFT, padx=2)
                
                # Favorite checkbox
                favorite_var = tk.BooleanVar(value=self.items[name].get("Favorite", False))
                favorite_check = tk.Checkbutton(top_row, text="★", variable=favorite_var)
                favorite_check.pack(side=tk.RIGHT)
                
                # Middle section: Stats and Effects
                middle_frame = tk.Frame(edit_frame)
                middle_frame.pack(fill=tk.X, pady=5)
                
                # Left side - Stats
                stats_frame = tk.Frame(middle_frame)
                stats_frame.pack(side=tk.LEFT, fill=tk.Y)
                
                # Stats entries
                stats = [
                    ("Price", self.items[name]["Price"]),
                    ("Adjustment", self.items[name]["Adjustment"]),
                    ("Effect Value", self.items[name].get("Effect Value", 0))
                ]
                
                stats_entries = {}
                for label, value in stats:
                    row = tk.Frame(stats_frame)
                    row.pack(fill=tk.X, pady=2)
                    tk.Label(row, text=f"{label}:").pack(side=tk.LEFT, padx=(0, 5))
                    entry = tk.Entry(row, width=10)
                    entry.insert(0, str(value))
                    entry.pack(side=tk.LEFT)
                    stats_entries[label.lower().replace(" ", "_")] = entry
                
                # Right side - Effects
                effects_frame = tk.Frame(middle_frame)
                effects_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))
                
                tk.Label(effects_frame, text="Effects:").pack(anchor="w")
                effects_text = tk.Text(effects_frame, height=3, width=40)
                effects_text.insert("1.0", self.items[name].get("Effects", ""))
                effects_text.pack(fill=tk.BOTH, expand=True)
                
                # Bottom section: Optional fields and buttons
                bottom_frame = tk.Frame(edit_frame)
                bottom_frame.pack(fill=tk.X, pady=(5, 0))
                
                # Optional fields dropdown and add button
                options_frame = tk.Frame(bottom_frame)
                options_frame.pack(side=tk.LEFT)
                
                optional_dropdown = ttk.Combobox(options_frame, values=OPTIONAL_FIELDS, state="readonly", width=20)
                optional_dropdown.set("Add field...")
                optional_dropdown.pack(side=tk.LEFT, padx=(0, 5))
                
                add_field_button = tk.Button(options_frame, text="+", width=3,
                                           command=lambda: self.add_optional_field(item_data, edit_frame, len(item_data["widgets"].get("optional_entries", {}))))
                add_field_button.pack(side=tk.LEFT)
                
                # Buttons frame
                buttons_frame = tk.Frame(bottom_frame)
                buttons_frame.pack(side=tk.RIGHT)
                
                # Delete button on left
                delete_button = tk.Button(buttons_frame, text="Delete", width=8,
                                        command=lambda n=name: self.delete_item(n),
                                        fg="red")
                delete_button.pack(side=tk.LEFT, padx=5)
                
                # Cancel and Confirm buttons
                confirm_button = tk.Button(buttons_frame, text="Confirm", width=8,
                                         command=lambda n=name: self.confirm_edit(n))
                confirm_button.pack(side=tk.RIGHT, padx=(5, 0))
                
                cancel_button = tk.Button(buttons_frame, text="Cancel", width=8,
                                        command=self.display_items)
                cancel_button.pack(side=tk.RIGHT)
                
                # Optional fields section (will be populated as needed)
                optional_fields_frame = tk.Frame(edit_frame)
                optional_fields_frame.pack(fill=tk.X, pady=(5, 0))
                
                # Store widgets
                item_data["widgets"].update({
                    "name_entry": name_entry,
                    "category_var": category_var,
                    "favorite_var": favorite_var,
                    "price_entry": stats_entries["price"],
                    "adjustment_entry": stats_entries["adjustment"],
                    "effect_value_entry": stats_entries["effect_value"],
                    "effects_text": effects_text,
                    "optional_dropdown": optional_dropdown,
                    "optional_fields_frame": optional_fields_frame,
                    "edit_frame": edit_frame,
                    "confirm_button": confirm_button,
                    "cancel_button": cancel_button,
                    "delete_button": delete_button,
                    "optional_entries": {}
                })
                
                # Add existing optional fields
                for field in OPTIONAL_FIELDS:
                    if field in self.items[name] and self.items[name][field] > 0:
                        self.create_optional_field_entry(optional_fields_frame, item_data, field, 
                                                      self.items[name][field])
                
                # Focus the name entry
                name_entry.focus_set()
                break

    def create_optional_field_entry(self, parent_frame, item_data, field_name, value):
        """Create an entry for an optional field in a horizontal layout"""
        frame = tk.Frame(parent_frame)
        frame.pack(fill=tk.X, pady=1)
        
        # Label on left
        tk.Label(frame, text=f"{field_name}:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Entry in middle (fixed width)
        entry = tk.Entry(frame, width=10)
        entry.insert(0, str(value))
        entry.pack(side=tk.LEFT)
        
        # Remove button on right
        def remove_field():
            frame.destroy()
            if "optional_entries" in item_data["widgets"]:
                if field_name in item_data["widgets"]["optional_entries"]:
                    del item_data["widgets"]["optional_entries"][field_name]
        
        remove_btn = tk.Button(frame, text="×", width=2, command=remove_field)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        # Store the widgets
        if "optional_entries" not in item_data["widgets"]:
            item_data["widgets"]["optional_entries"] = {}
        item_data["widgets"]["optional_entries"][field_name] = {"frame": frame, "entry": entry}

    def add_optional_field(self, item_data, parent_frame, current_row):
        """Add a new optional field entry"""
        field_name = item_data["widgets"]["optional_dropdown"].get()
        if field_name == "Add field..." or field_name == "Select field to add":
            return
        
        # Check if field already exists
        if ("optional_entries" in item_data["widgets"] and 
            field_name in item_data["widgets"]["optional_entries"]):
            return
        
        # Create the new field entry
        self.create_optional_field_entry(item_data["widgets"]["optional_fields_frame"], 
                                       item_data, field_name, 0)

    def confirm_edit(self, name):
        """Confirm an item edit"""
        # Find the item frame
        for item_frame in self.list_frame.winfo_children():
            if hasattr(item_frame, "item_data") and item_frame.item_data["name"] == name:
                item_data = item_frame.item_data
                
                # Get the new values
                new_name = item_data["widgets"]["name_entry"].get()
                new_price = item_data["widgets"]["price_entry"].get()
                new_adjustment = item_data["widgets"]["adjustment_entry"].get()
                new_effect_value = item_data["widgets"]["effect_value_entry"].get()
                new_effects = item_data["widgets"]["effects_text"].get("1.0", tk.END).strip()
                new_favorite = item_data["widgets"]["favorite_var"].get()
                new_category = item_data["widgets"]["category_var"].get() or Category.NONE
                
                # Validate the new values
                if not self.validate_input(new_name, new_price, new_adjustment, new_effect_value):
                    return
                
                if new_name != name and new_name in self.items:
                    messagebox.showerror("Validation Error", f"Item '{new_name}' already exists")
                    return

                # Create new item data with required fields
                new_item_data = {
                    "Price": int(new_price),
                    "Adjustment": int(new_adjustment),
                    "Effect Value": int(new_effect_value),
                    "Effects": new_effects,
                    "Favorite": new_favorite,
                    "Category": new_category
                }

                # Add optional fields that have values > 0
                if "optional_entries" in item_data["widgets"]:
                    for field, widgets in item_data["widgets"]["optional_entries"].items():
                        try:
                            value = int(widgets["entry"].get())
                            if value > 0:
                                new_item_data[field] = value
                        except ValueError:
                            messagebox.showerror("Validation Error", 
                                               f"Invalid value for {field}. Must be a positive integer.")
                            return
                
                # Update the item
                if new_name != name:
                    # Create a new item with the new name
                    self.items[new_name] = new_item_data
                    # Delete the old item
                    del self.items[name]
                else:
                    # Update the existing item
                    self.items[name] = new_item_data
                
                # Save the changes
                self.save_items()
                
                # Refresh the display
                self.display_items()
                break
    
    def add_item(self):
        """Add a new item"""
        name = self.new_name_entry.get()
        price = self.new_price_entry.get()
        adjustment = self.new_weight_entry.get()
        effect_value = self.new_effect_weight_entry.get()
        effects = self.new_effects_text.get("1.0", tk.END).strip()
        
        # Validate input
        if not self.validate_input(name, price, adjustment, effect_value):
            return
        
        # Check if the item already exists
        if name in self.items:
            messagebox.showerror("Validation Error", f"Item '{name}' already exists")
            return
        
        # Add the item
        self.items[name] = {
            "Price": int(price),
            "Adjustment": int(adjustment),
            "Effect Value": int(effect_value),
            "Effects": effects
        }
        
        # Save the changes
        self.save_items()
        
        # Clear the entries
        self.new_name_entry.delete(0, tk.END)
        self.new_price_entry.delete(0, tk.END)
        self.new_weight_entry.delete(0, tk.END)
        self.new_effect_weight_entry.delete(0, tk.END)
        self.new_effect_weight_entry.insert(0, "0")  # Reset to default
        self.new_effects_text.delete("1.0", tk.END)
        
        # Refresh the display
        self.display_items()

    def delete_item(self, name):
        """Delete an item after confirmation"""
        # Show confirmation dialog
        confirm = messagebox.askyesno("Confirm Delete", 
                                    f"Are you sure you want to delete {name}?",
                                    icon='warning')
        
        if confirm:
            # Delete the item
            if name in self.items:
                del self.items[name]
                # Save the changes
                self.save_items()
                # Refresh the display
                self.display_items()

    def setup_new_item_frame(self):
        """Setup the new item frame"""
        # New item frame (at the bottom)
        self.new_item_frame = tk.Frame(self.items_frame, bd=1, relief=tk.GROOVE)
        self.new_item_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # New item entries
        tk.Label(self.new_item_frame, text="Add New Item:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        entry_frame = tk.Frame(self.new_item_frame)
        entry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(entry_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.new_name_entry = tk.Entry(entry_frame, width=30)
        self.new_name_entry.grid(row=0, column=1, sticky="w", pady=2, padx=5)
        
        tk.Label(entry_frame, text="Price:").grid(row=1, column=0, sticky="w", pady=2)
        self.new_price_entry = tk.Entry(entry_frame, width=15)
        self.new_price_entry.grid(row=1, column=1, sticky="w", pady=2, padx=5)
        
        tk.Label(entry_frame, text="Adjustment:").grid(row=2, column=0, sticky="w", pady=2)
        self.new_weight_entry = tk.Entry(entry_frame, width=15)
        self.new_weight_entry.grid(row=2, column=1, sticky="w", pady=2, padx=5)

        tk.Label(entry_frame, text="Effect Value:").grid(row=3, column=0, sticky="w", pady=2)
        self.new_effect_weight_entry = tk.Entry(entry_frame, width=15)
        self.new_effect_weight_entry.insert(0, "0")  # Default value
        self.new_effect_weight_entry.grid(row=3, column=1, sticky="w", pady=2, padx=5)

        tk.Label(entry_frame, text="Effects:").grid(row=4, column=0, sticky="nw", pady=2)
        self.new_effects_text = tk.Text(entry_frame, width=30, height=4)
        self.new_effects_text.grid(row=4, column=1, sticky="w", pady=2, padx=5)
        
        # Buttons frame
        btn_frame = tk.Frame(self.new_item_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.add_button = tk.Button(btn_frame, text="Add Item", command=self.add_item, width=10)
        self.add_button.pack(side=tk.RIGHT)
        
        # Configure canvas for scrolling
        self.items_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def setup_sidebar(self):
        """Setup the sidebar with weight controls"""
        # Title for weights section
        tk.Label(self.sidebar, text="Weights", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Get all weight fields
        weight_fields = ['Adjustment', 'Effect Value'] + OPTIONAL_FIELDS
        
        # Create controls for each weight
        for field in weight_fields:
            # Main frame for this weight control row
            frame = tk.Frame(self.sidebar)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Label on the left
            tk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            
            # Container frame for right-aligned elements
            right_container = tk.Frame(frame)
            right_container.pack(side=tk.RIGHT)
            
            # Buttons frame inside right container
            btn_frame = tk.Frame(right_container)
            btn_frame.pack(side=tk.RIGHT)
            
            # Increment/decrement buttons
            tk.Button(btn_frame, text="+", width=3,
                     command=lambda f=field: self.adjust_weight(f, True)).pack(side=tk.RIGHT, padx=1)
            tk.Button(btn_frame, text="-", width=3,
                     command=lambda f=field: self.adjust_weight(f, False)).pack(side=tk.RIGHT, padx=1)
            
            # Entry with StringVar - placed to left of buttons in right container
            self.weight_vars[field] = tk.StringVar(value="1.00")
            self.weight_vars[field].trace('w', lambda *args, f=field: self.on_weight_change(f, *args))
            entry = tk.Entry(right_container, textvariable=self.weight_vars[field], width=8)
            entry.pack(side=tk.RIGHT, padx=2)

    def find_optimal_items(self):
        """Find and display the optimal items for the given budget"""
        try:
            budget = int(self.search_var.get().strip())
            if budget < 3500:
                messagebox.showerror("Error", "Budget must be at least 3500")
                return
                
            from sack import find_optimal_items
            
            # Get optimal items
            optimal_items, total_price, total_weight = find_optimal_items(budget, self.items)
            
            # Store the optimal items list
            self.optimal_items = optimal_items
            self.showing_optimal = True
            
            # Clear the search field
            self.search_var.set("")
            
            # Update the display to show only optimal items
            self.display_items()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer budget (≥ 3500)")

    def reset_view(self):
        """Reset to normal view"""
        self.showing_optimal = False
        self.optimal_items = []
        self.display_items()
        
        # Hide the Reset button
        self.reset_button.pack_forget()

    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            # Only handle root window resizes
            available_width = event.width - 20  # Reduced padding allowance
            # Calculate how many columns can fit
            columns = max(1, min(8, available_width // (self.CARD_WIDTH + 2 * self.CARD_PADDING)))
            if columns != self.current_columns:
                self.current_columns = columns
                self.display_items()

    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar"""
        if self.hide_weights.get():
            self.sidebar.pack_forget()
            # Give more room to the main frame by removing right padding
            self.main_frame.pack_configure(padx=(4, 0))
        else:
            # Restore original padding when showing sidebar
            self.main_frame.pack_configure(padx=4)
            self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
        
        # Force a redraw to adjust the layout
        self.root.update_idletasks()
        self.display_items()

    def check_and_find_optimal_items(self):
        """Check if search text is a valid budget and find optimal items"""
        search_text = self.search_var.get().strip()
        try:
            budget = int(search_text)
            if budget >= 3500:
                self.find_optimal_items()
        except ValueError:
            # Not a valid budget, do nothing
            pass

def main():
    root = tk.Tk()
    app = ItemManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()