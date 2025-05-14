"""Weight sidebar component for adjusting item weights."""
import tkinter as tk
from typing import Dict, Callable
from utils.constants import OptionalField
from utils.validators import validate_weight_input, round_to_nearest_fraction

class WeightSidebar(tk.Frame):
    """Sidebar component for adjusting item weights."""

    def __init__(self, parent: tk.Widget, on_weight_change: Callable[[str, float], None]):
        """Initialize the weight sidebar.
        
        Args:
            parent: Parent widget
            on_weight_change: Callback for when a weight value changes
        """
        super().__init__(parent, bd=1, relief=tk.SOLID)
        self.on_weight_change = on_weight_change
        
        # State for increment tracking
        self.increment = 1.0
        self.last_field = None
        self.last_increment = None
        self.repeats = 0
        self.untouched = True
        
        # Weight variables
        self.weight_vars: Dict[str, tk.StringVar] = {}
        
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        # Title
        tk.Label(self, text="Weights", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Get all weight fields
        weight_fields = ['Adjustment', 'Effect Value'] + [f.value for f in OptionalField]
        
        # Create controls for each weight
        for field in weight_fields:
            self._create_weight_control(field)

    def _create_weight_control(self, field: str):
        """Create a weight control row.
        
        Args:
            field: Name of the weight field
        """
        # Main frame for this weight control row
        frame = tk.Frame(self)
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
                 command=lambda: self._adjust_weight(field, True)).pack(side=tk.RIGHT, padx=1)
        tk.Button(btn_frame, text="-", width=3,
                 command=lambda: self._adjust_weight(field, False)).pack(side=tk.RIGHT, padx=1)
        
        # Entry with StringVar
        self.weight_vars[field] = tk.StringVar(value="1.00")
        self.weight_vars[field].trace('w', lambda *args, f=field: self._on_weight_change(f))
        entry = tk.Entry(right_container, textvariable=self.weight_vars[field], width=8)
        entry.pack(side=tk.RIGHT, padx=2)

    def _adjust_weight(self, field: str, is_increment: bool):
        """Adjust a weight value using dynamic increment system.
        
        Args:
            field: Name of the weight field
            is_increment: True for increment, False for decrement
        """
        try:
            # Handle field switching
            if field != self.last_field:
                self.untouched = True
                self.last_field = field

            current = float(self.weight_vars[field].get())

            # Update repeats counter
            if self.untouched:
                self.repeats = -2
                self.untouched = False
            elif is_increment == self.last_increment:
                self.repeats += 1
            else:
                self.repeats -= 2

            # Clamp repeats
            self.repeats = max(min(self.repeats, 15), -15)
            
            # Map repeats to increment value
            index_from_repeats = int((self.repeats + 15) / 2)
            
            # Predefined increment values
            possible_increments = [0.05, 0.1, 0.2, 0.33, 0.5, 0.75, 1.0, 
                                 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 8.0]
            
            # Select and apply increment
            increment = possible_increments[index_from_repeats]
            if not is_increment:
                increment *= -1
                
            new_value = current + increment
            new_value = round_to_nearest_fraction(new_value)

            # Store state for next press
            self.last_increment = is_increment

            # Update UI and notify
            self.weight_vars[field].set(f"{new_value:.2f}")
            self.on_weight_change(field, new_value)
            
        except ValueError:
            pass  # Ignore invalid values

    def _on_weight_change(self, field: str, *args):
        """Handle manual changes to weight values.
        
        Args:
            field: Name of the weight field
            *args: Additional arguments from trace callback
        """
        try:
            value = self.weight_vars[field].get()
            valid, float_val = validate_weight_input(value)
            
            if valid:
                # Round and normalize
                float_val = round_to_nearest_fraction(float_val)
                
                # Update display and notify
                self.weight_vars[field].set(f"{float_val:.2f}")
                self.on_weight_change(field, float_val)
        except ValueError:
            pass  # Ignore invalid input

    def set_weight(self, field: str, value: float):
        """Set a weight value.
        
        Args:
            field: Name of the weight field
            value: New weight value
        """
        if field in self.weight_vars:
            self.weight_vars[field].set(f"{value:.2f}")

    def get_weights(self) -> Dict[str, float]:
        """Get all current weight values.
        
        Returns:
            Dictionary of weight values
        """
        weights = {}
        for field, var in self.weight_vars.items():
            try:
                weights[field] = float(var.get())
            except ValueError:
                weights[field] = 1.0
        return weights 