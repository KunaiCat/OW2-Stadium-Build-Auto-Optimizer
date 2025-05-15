"""Custom weights editor component for creating and editing weight profiles."""
import tkinter as tk
from typing import Dict, Callable, Optional
from ui.weight_sidebar import WeightSidebar

class CustomWeightsEditor(tk.Frame):
    """Dialog for creating and editing custom weight profiles."""

    def __init__(self, parent: tk.Widget, 
                 profile_name: str, 
                 weights: Dict[str, float],
                 on_save: Callable[[str, Dict[str, float]], None],
                 on_delete: Optional[Callable[[str], None]] = None):
        """Initialize the custom weights editor.
        
        Args:
            parent: Parent widget
            profile_name: Name of the weight profile (empty for new profiles)
            weights: Initial weights dictionary
            on_save: Callback for saving weights (receives name and weights dict)
            on_delete: Optional callback for deleting a profile
        """
        super().__init__(parent)
        self.parent = parent
        self.profile_name = profile_name
        self.initial_weights = weights
        self.on_save = on_save
        self.on_delete = on_delete
        self.is_new = not profile_name
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Top section - name entry
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(top_frame, text="Profile Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_entry = tk.Entry(top_frame, width=30)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if self.profile_name:
            self.name_entry.insert(0, self.profile_name)
        
        # Scale factor section - Min and Max entries
        scale_frame = tk.Frame(self)
        scale_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Min Entry
        min_frame = tk.Frame(scale_frame)
        min_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(min_frame, text="Min:").pack(side=tk.LEFT, padx=(0, 5))
        self.min_entry = tk.Entry(min_frame, width=8)
        self.min_entry.pack(side=tk.LEFT)
        self.min_entry.insert(0, "0.1")  # Default min value
        
        # Max Entry
        max_frame = tk.Frame(scale_frame)
        max_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        tk.Label(max_frame, text="Max:").pack(side=tk.LEFT, padx=(10, 5))
        self.max_entry = tk.Entry(max_frame, width=8)
        self.max_entry.pack(side=tk.LEFT)
        self.max_entry.insert(0, "2.0")  # Default max value
        
        # If this is an existing profile, set min/max from existing values
        if self.profile_name and "_min" in self.initial_weights and "_max" in self.initial_weights:
            self.min_entry.delete(0, tk.END)
            self.min_entry.insert(0, str(self.initial_weights["_min"]))
            self.max_entry.delete(0, tk.END)
            self.max_entry.insert(0, str(self.initial_weights["_max"]))
        
        # Middle section - weights sidebar
        self.weights_sidebar = WeightSidebar(self, on_weight_change=self._on_temp_weight_change)
        self.weights_sidebar.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Set initial weights
        for field, value in self.initial_weights.items():
            if field not in ["_enabled", "_min", "_max", "_scale"]:
                self.weights_sidebar.set_weight(field, value)
        
        # Bottom section - buttons
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Delete button (only for existing profiles)
        if not self.is_new and self.on_delete:
            delete_btn = tk.Button(bottom_frame, text="Delete", fg="red",
                               command=self._delete_profile)
            delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel and Confirm buttons
        cancel_btn = tk.Button(bottom_frame, text="Cancel",
                           command=self.parent.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        confirm_btn = tk.Button(bottom_frame, text="Confirm",
                            command=self._confirm_edit)
        confirm_btn.pack(side=tk.RIGHT, padx=5)
    
    def _on_temp_weight_change(self, field: str, value: float):
        """Temporary weight change handler (doesn't save until confirmed)."""
        # Just update the UI, don't save to file
        pass
    
    def _confirm_edit(self):
        """Handle confirm button press."""
        name = self.name_entry.get().strip()
        if not name:
            tk.messagebox.showerror("Error", "Profile name cannot be empty")
            return
        
        # Get current weights from sidebar
        weights = self.weights_sidebar.get_weights()
        
        # Add min and max values
        try:
            min_val = float(self.min_entry.get())
            max_val = float(self.max_entry.get())
            if min_val <= 0:
                tk.messagebox.showerror("Error", "Min value must be greater than 0")
                return
            if max_val <= min_val:
                tk.messagebox.showerror("Error", "Max value must be greater than Min value")
                return
            weights["_min"] = min_val
            weights["_max"] = max_val
            weights["_scale"] = 0.5  # Default scale (middle of slider)
        except ValueError:
            tk.messagebox.showerror("Error", "Min and Max must be valid numbers")
            return
        
        # Call save callback
        self.on_save(name, weights)
        
        # Close dialog
        self.parent.destroy()
    
    def _delete_profile(self):
        """Handle delete button press."""
        if tk.messagebox.askyesno("Confirm Delete", 
                                f"Are you sure you want to delete the '{self.profile_name}' weight profile?"):
            if self.on_delete:
                self.on_delete(self.profile_name)
            self.parent.destroy() 