import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ui.weight_sidebar import WeightSidebar
from ui.main_window import SearchWindow
from ui.item_list import ItemList
from ui.custom_weights_editor import CustomWeightsEditor
from services.item_service import ItemService
from services.optimizer import OptimizerService
from utils.constants import UIConstant, Style

class MainMenu:
    def __init__(self, item_service: ItemService, optimizer_service: OptimizerService):
        self.root = tk.Tk()
        self.root.title("Main Menu")
        self.root.geometry("1100x700")
        self.root.configure(bg=Style.BG_DARK)
        self.item_service = item_service
        self.optimizer_service = optimizer_service
        self.optimal_items = None

        # Configure ttk styles
        self.style = ttk.Style()
        self.style.configure("Treeview", **Style.TREEVIEW)
        self.style.configure("Treeview.Heading", 
                           background=Style.BG_LIGHTER,
                           foreground=Style.FG_MAIN,
                           relief="flat")

        # Create main horizontal split between content and sidebar
        self.main_split = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, 
                                       bg=Style.BORDER, 
                                       sashwidth=4,
                                       sashpad=1)
        self.main_split.pack(fill=tk.BOTH, expand=True)

        # Left side - Main content area (52.5% of window)
        self.main_content_frame = tk.Frame(self.main_split, **Style.FRAME_NORMAL)
        self.main_split.add(self.main_content_frame, width=578)

        # Budget controls container - positioned at 7% height
        self.budget_container = tk.Frame(self.main_content_frame, **Style.FRAME_NORMAL)
        self.budget_container.pack(fill=tk.X, pady=(50, 0))

        budget_center_frame = tk.Frame(self.budget_container, **Style.FRAME_NORMAL)
        budget_center_frame.pack(anchor='center')
        
        # Create a modified style without font
        label_style = {k: v for k, v in Style.LABEL_NORMAL.items() if k != 'font'}
        budget_label = tk.Label(budget_center_frame, text="Budget:", 
                              font=Style.FONT_LARGE, **label_style)
        budget_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.budget_var = tk.StringVar()
        # Create a modified style without font
        entry_style = {k: v for k, v in Style.ENTRY_NORMAL.items() if k != 'font'}
        self.budget_entry = tk.Entry(budget_center_frame, 
                                   textvariable=self.budget_var,
                                   width=12,
                                   font=Style.FONT_LARGE,
                                   **entry_style)
        self.budget_entry.pack(side=tk.LEFT)
        
        btn_size = 80
        btn_frame = tk.Frame(budget_center_frame, width=btn_size, height=btn_size,
                           **Style.FRAME_NORMAL)
        btn_frame.pack(side=tk.LEFT, padx=(15,0))
        btn_frame.pack_propagate(False)
        
        # Create a modified style without font
        btn_style = {k: v for k, v in Style.BTN_ACCENT.items() if k != 'font'}
        self.find_btn = tk.Button(btn_frame, text="Find\nItems",
                                command=self.find_items,
                                font=Style.FONT_LARGE,
                                **btn_style)
        self.find_btn.pack(fill=tk.BOTH, expand=True)

        # Error message for budget
        self.budget_error = tk.Label(self.main_content_frame, text="",
                                   fg=Style.ERROR,
                                   font=Style.FONT_MAIN,
                                   bg=Style.BG_DARK)
        self.budget_error.pack(anchor='center', pady=(0, 5))

        # Container for reset button and item cards - adjust padding to be closer to budget entry
        self.cards_container = tk.Frame(self.main_content_frame, **Style.FRAME_NORMAL)
        self.cards_container.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Create a frame for the search button at the bottom-right
        search_frame = tk.Frame(self.main_content_frame, **Style.FRAME_NORMAL)
        search_frame.pack(side=tk.BOTTOM, anchor='se', padx=10, pady=10)
        tk.Button(search_frame, text="Search",
                 width=12,
                 command=self.open_search,
                 **Style.BTN_NORMAL).pack()

        # Right side - Sidebar
        self.sidebar = tk.Frame(self.main_split, bg=Style.BG_DARK)
        self.main_split.add(self.sidebar, width=522)  # Combined width of both right panes
        
        # Create horizontal split in the sidebar
        self.sidebar_split = tk.PanedWindow(self.sidebar, orient=tk.HORIZONTAL,
                                          bg=Style.BORDER,
                                          sashwidth=4,
                                          sashpad=1)
        self.sidebar_split.pack(fill=tk.BOTH, expand=True)
        
        # Configure ttk styles for treeview and other widgets
        style = ttk.Style()
        
        # Configure slider style
        style.configure("Custom.Horizontal.TScale",
                      background=Style.BG_DARK,
                      troughcolor=Style.BG_DARKER,
                      lightcolor=Style.BG_DARK,
                      darkcolor=Style.BG_DARK)
        
        # Left side of sidebar - Custom Weight Sets (30% of window)
        self.sidebar_left = tk.Frame(self.sidebar_split, bg=Style.BG_DARK)
        self.sidebar_split.add(self.sidebar_left, width=330)
        
        # Add title to left side
        tk.Label(self.sidebar_left, text="Weight Profiles",
                **Style.LABEL_TITLE).pack(pady=10)
        
        # Base Weights button - cannot be removed
        self.base_weights_btn = tk.Button(self.sidebar_left, text="Base Weights",
                                        width=15,
                                        command=self.open_base_weights,
                                        **Style.BTN_NORMAL)
        self.base_weights_btn.pack(pady=5)
        
        # Custom weights section
        self.custom_weights_frame = tk.Frame(self.sidebar_left, **Style.FRAME_NORMAL)
        self.custom_weights_frame.pack(fill=tk.X, expand=True, pady=5)
        
        # Bottom buttons frame
        bottom_buttons_frame = tk.Frame(self.sidebar_left, **Style.FRAME_NORMAL)
        bottom_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Calculate weights button
        self.calc_weights_btn = tk.Button(bottom_buttons_frame, text="Calculate Weights",
                                        width=15,
                                        command=self.calculate_weights,
                                        **Style.BTN_ACCENT)
        self.calc_weights_btn.pack(pady=5)
        
        # Add button for new custom weights
        self.add_weights_btn = tk.Button(bottom_buttons_frame, text="+",
                                       width=5,
                                       command=self.add_custom_weights,
                                       **Style.BTN_NORMAL)
        self.add_weights_btn.pack(pady=5)

        # Right side of sidebar - Output Weights Table (17.5% of window)
        self.sidebar_right = tk.Frame(self.sidebar_split, bg=Style.BG_DARK)
        self.sidebar_split.add(self.sidebar_right, width=192)
        
        # Output weights title
        tk.Label(self.sidebar_right, text="Output Weights",
                **Style.LABEL_TITLE).pack(pady=10)
        
        # Create frame to hold treeview and scrollbar with dark background
        tree_frame = tk.Frame(self.sidebar_right, bg=Style.BG_DARK)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Configure ttk styles for treeview
        style = ttk.Style()
        style.layout("Custom.Treeview", [
            ('Custom.Treeview.treearea', {'sticky': 'nswe'})
        ])
        style.configure("Custom.Treeview",
                      background=Style.BG_DARK,
                      foreground=Style.FG_MAIN,
                      fieldbackground=Style.BG_DARK,
                      borderwidth=0,
                      relief="flat")
        
        # Configure the heading style
        style.layout("Custom.Treeview.Heading", [
            ("Custom.Treeview.Heading.cell", {'sticky': 'nswe'}),
            ("Custom.Treeview.Heading.border", {'sticky': 'nswe', 'children': [
                ("Custom.Treeview.Heading.padding", {'sticky': 'nswe', 'children': [
                    ("Custom.Treeview.Heading.image", {'side': 'right', 'sticky': ''}),
                    ("Custom.Treeview.Heading.text", {'sticky': 'we'})
                ]})
            ]})
        ])
        style.configure("Custom.Treeview.Heading",
                      background=Style.BG_DARKER,
                      foreground=Style.FG_MAIN,
                      relief="flat",
                      borderwidth=0)
        style.map("Custom.Treeview.Heading",
                 background=[("active", Style.BG_LIGHTER)],
                 relief=[("active", "flat")])
        
        style.map("Custom.Treeview",
                 background=[("selected", Style.ACCENT)],
                 foreground=[("selected", Style.FG_MAIN)])
        
        # Configure scrollbar style
        style.configure("Custom.Vertical.TScrollbar",
                      background=Style.BG_DARK,
                      troughcolor=Style.BG_DARKER,
                      borderwidth=0,
                      arrowcolor=Style.FG_MAIN)
        
        # Create treeview with custom style
        self.output_weights_tree = ttk.Treeview(tree_frame,
                                              columns=("Weight", "Value"),
                                              show="headings",
                                              height=15,
                                              style="Custom.Treeview")
        
        self.output_weights_tree.heading("Weight", text="Weight")
        self.output_weights_tree.heading("Value", text="Value")
        self.output_weights_tree.column("Weight", width=120)
        self.output_weights_tree.column("Value", width=80)
        self.output_weights_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar with custom style
        scrollbar = ttk.Scrollbar(tree_frame,
                               orient=tk.VERTICAL,
                               style="Custom.Vertical.TScrollbar",
                               command=self.output_weights_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_weights_tree.configure(yscrollcommand=scrollbar.set)

        # Track custom weight profiles vars
        self.weight_profile_vars = {}
        self.weight_profile_buttons = {}
        self.weight_profile_sliders = {}
        self.weight_profile_scale_vars = {}
        
        # Load existing weight profiles and update output weights table
        self.refresh_weight_profiles()
        self.update_output_weights_table()

        # Bind events
        self.budget_entry.bind('<Key>', self.clear_budget_error)
        self.root.bind('<FocusIn>', self._on_window_focus_in)
        self.budget_entry.bind('<Return>', lambda event: self.find_items())

        self.reset_btn = None
        self.item_list = None

    def open_search(self):
        win = tk.Toplevel(self.root)
        win.title("Search")
        win.geometry("1024x800")
        SearchWindow(win, self.item_service, self.optimizer_service)

    def open_base_weights(self):
        win = tk.Toplevel(self.root)
        win.title("Base Weights")
        win.geometry("300x600")
        
        # Use a callback that doesn't automatically recalculate
        def on_weight_change(field, value):
            self.item_service.update_weight(field, value, recalculate=False)
            
        sidebar = WeightSidebar(win, on_weight_change=on_weight_change)
        sidebar.pack(fill=tk.BOTH, expand=True)
        for field, value in self.item_service.weights["Base Weights"].items():
            if field != "_enabled":
                sidebar.set_weight(field, value)
            
    def add_custom_weights(self):
        """Open dialog to create a new custom weight profile"""
        # Create popup window
        win = tk.Toplevel(self.root)
        win.title("New Weight Profile")
        win.geometry("400x700")
        win.transient(self.root)
        win.grab_set()
        
        # Use the base weights as a template for the new profile
        base_weights = {k: v for k, v in self.item_service.weights["Base Weights"].items() 
                        if k != "_enabled"}
        
        # Create editor
        editor = CustomWeightsEditor(win, "", base_weights, self._on_save_weight_profile)
        editor.pack(fill=tk.BOTH, expand=True)
    
    def edit_custom_weights(self, profile_name):
        """Open dialog to edit an existing custom weight profile"""
        if profile_name not in self.item_service.weights:
            return
            
        # Create popup window
        win = tk.Toplevel(self.root)
        win.title(f"Edit Weight Profile: {profile_name}")
        win.geometry("400x700")
        win.transient(self.root)
        win.grab_set()
        
        # Get current weights and remove internal flags
        weights = {k: v for k, v in self.item_service.weights[profile_name].items() 
                  if k != "_enabled"}
        
        # Create editor
        editor = CustomWeightsEditor(
            win, 
            profile_name, 
            weights, 
            self._on_save_weight_profile,
            self._on_delete_weight_profile
        )
        editor.pack(fill=tk.BOTH, expand=True)
    
    def _on_save_weight_profile(self, profile_name, weights):
        """Handle saving a weight profile"""
        # Check for name conflicts
        if profile_name != "Base Weights" and profile_name in self.item_service.weights:
            # It's an update
            old_enabled = profile_name in self.item_service.enabled_profiles
            self.item_service.add_or_update_weight_profile(profile_name, weights)
            # Preserve enabled state
            self.item_service.toggle_weight_profile(profile_name, old_enabled)
        else:
            # It's a new profile
            self.item_service.add_or_update_weight_profile(profile_name, weights)
            
        # Refresh sidebar
        self.refresh_weight_profiles()
    
    def _on_delete_weight_profile(self, profile_name):
        """Handle deleting a weight profile"""
        if profile_name == "Base Weights":
            messagebox.showerror("Error", "Cannot delete Base Weights profile")
            return
            
        if self.item_service.delete_weight_profile(profile_name):
            # Refresh sidebar
            self.refresh_weight_profiles()
    
    def refresh_weight_profiles(self):
        """Refresh the display of weight profiles."""
        # Clear existing profile displays
        for widget in self.custom_weights_frame.winfo_children():
            widget.destroy()
        
        # Clear tracking dictionaries
        self.weight_profile_vars.clear()
        self.weight_profile_buttons.clear()
        self.weight_profile_sliders.clear()
        self.weight_profile_scale_vars.clear()
        
        # Add each custom weight profile
        for profile_name, weights in self.item_service.weights.items():
            if profile_name != "Base Weights":
                # Create frame for this profile
                profile_frame = tk.Frame(self.custom_weights_frame, bg=Style.BG_DARK)
                profile_frame.pack(fill=tk.X, pady=2)
                
                # Left side - checkbox and button
                left_frame = tk.Frame(profile_frame, bg=Style.BG_DARK)
                left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Create checkbox var and add to tracking dict
                var = tk.BooleanVar(value=weights.get("_enabled", False))
                self.weight_profile_vars[profile_name] = var
                
                # Create and pack checkbox
                cb = tk.Checkbutton(left_frame, text=profile_name,
                                  variable=var,
                                  command=lambda name=profile_name: self.toggle_profile(name),
                                  selectcolor=Style.BG_DARKER,
                                  bg=Style.BG_DARK,
                                  fg=Style.FG_MAIN,
                                  activebackground=Style.BG_DARK,
                                  activeforeground=Style.FG_MAIN)
                cb.pack(side=tk.LEFT)
                
                # Create and pack edit button
                btn = tk.Button(left_frame, text="Edit",
                              width=6,
                              command=lambda name=profile_name: self.edit_custom_weights(name),
                              **Style.BTN_NORMAL)
                btn.pack(side=tk.RIGHT, padx=2)
                self.weight_profile_buttons[profile_name] = btn
                
                # Create scale variable and add to tracking dict
                scale_var = tk.DoubleVar(value=weights.get("_scale", 0.5))
                self.weight_profile_scale_vars[profile_name] = scale_var
                
                # Create slider frame
                slider_frame = tk.Frame(profile_frame, bg=Style.BG_DARK)
                slider_frame.pack(fill=tk.X, pady=(0, 5))
                
                # Create and pack slider with custom style
                slider = ttk.Scale(slider_frame, from_=0, to=100,
                                 orient=tk.HORIZONTAL,
                                 variable=scale_var,
                                 command=lambda val, name=profile_name: self.adjust_profile_scale(name),
                                 style="Custom.Horizontal.TScale")
                slider.pack(fill=tk.X, padx=5)
                self.weight_profile_sliders[profile_name] = slider
                
                # Set initial slider state based on checkbox
                if not var.get():
                    slider.config(state=tk.DISABLED)
        
        # Update the output weights table
        self.update_output_weights_table()

    def update_profile_scale(self, profile_name, scale_value):
        """Update the scale factor for a weight profile"""
        if profile_name in self.item_service.weights:
            self.item_service.weights[profile_name]["_scale"] = scale_value
            self.item_service.save_data()
    
    def toggle_profile(self, profile_name: str):
        """Toggle a weight profile on/off."""
        is_enabled = self.weight_profile_vars[profile_name].get()
        
        # Update both the _enabled flag and the enabled_profiles set
        self.item_service.weights[profile_name]["_enabled"] = is_enabled
        if is_enabled:
            self.item_service.enabled_profiles.add(profile_name)
        else:
            self.item_service.enabled_profiles.discard(profile_name)
        
        # Enable/disable the slider based on checkbox state
        if is_enabled:
            self.weight_profile_sliders[profile_name].config(state=tk.NORMAL)
        else:
            self.weight_profile_sliders[profile_name].config(state=tk.DISABLED)
        
        # Save changes but don't recalculate - that only happens on Calculate button press
        self.item_service.save_data()

    def adjust_profile_scale(self, profile_name: str, *args):
        """Adjust the scale factor for a weight profile."""
        # Get scale value (0-100) and convert to 0-1 range
        scale_value = self.weight_profile_scale_vars[profile_name].get() / 100.0
        
        # Update the scale value in the weights dictionary
        self.item_service.weights[profile_name]["_scale"] = scale_value
        
        # Save changes but don't recalculate - that only happens on Calculate button press
        self.item_service.save_data()

    def find_items(self):
        self.find_btn.config(bg=Style.SUCCESS)  # Use styled success color
        self.root.after(1000, self._delayed_find_items)

    def _delayed_find_items(self):
        budget_str = self.budget_var.get().strip()
        try:
            budget = int(budget_str)
            if budget < 3500:
                raise ValueError
        except ValueError:
            self.flash_budget_error()
            self.find_btn.config(bg=Style.ACCENT)  # Reset to accent color
            return
        self.clear_budget_error()
        # Ensure all items are recalculated with the latest output weights
        self.item_service.recalculate_weights()
        optimal_items, total_price, total_weight = self.optimizer_service.find_optimal_items(budget, self.item_service.items)
        print(f"Found optimal items: {optimal_items}")
        print(f"Total price: {total_price}, Total weight: {total_weight}")
        self.optimal_items = optimal_items
        self.show_optimal_items()

    def flash_budget_error(self):
        self.budget_entry.config(bg=Style.ERROR)
        self.budget_error.config(text="Please enter an integer budget of at least 3500.")
        self.root.after(200, lambda: self.budget_entry.config(bg=Style.BG_DARKER))

    def clear_budget_error(self, event=None):
        self.budget_entry.config(bg=Style.BG_DARKER)
        self.budget_error.config(text="")

    def show_optimal_items(self):
        """Display the optimal items in the UI."""
        print("Showing optimal items...")
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        print(f"Cards container after clearing: {self.cards_container.winfo_children()}")
        
        # Reset button background to normal after showing items
        self.find_btn.config(bg=Style.ACCENT)
        if self.optimal_items:
            print(f"Have optimal items: {self.optimal_items}")
            self.reset_btn = tk.Button(self.cards_container, text="Reset",
                                     command=self.reset_optimal,
                                     **Style.BTN_NORMAL)
            self.reset_btn.pack(anchor="ne", pady=(0, 5), padx=10)
            # Sort items: Weapon, then Ability, then Survival; most expensive first within each
            items = [self.item_service.get_item(name) for name in self.optimal_items]
            print(f"Retrieved items: {[item.name for item in items if item]}")
            def cat_order(item):
                if item.category == 'Weapon': return 0
                if item.category == 'Ability': return 1
                if item.category == 'Survival': return 2
                return 3
            items_sorted = sorted(
                [item for item in items if item],
                key=lambda x: (cat_order(x), -x.price)
            )
            print(f"Sorted items: {[item.name for item in items_sorted]}")
            items_dict = {item.name: item for item in items_sorted}
            print("Creating ItemList...")
            # Create ItemList without triggering recalculation
            self.item_list = ItemList(self.cards_container, on_edit=self._on_edit_item)
            self.item_list.pack(fill=tk.BOTH, expand=True)
            print("Displaying items...")
            self.item_list.display_items(items_dict)
            print(f"Cards container after displaying: {self.cards_container.winfo_children()}")
        else:
            print("No optimal items to show")
            self.reset_btn = None
            self.item_list = None

    def _on_edit_item(self, name):
        item = self.item_service.get_item(name)
        if item:
            self._open_item_editor_popup(name, item)

    def _open_item_editor_popup(self, name, item):
        editor_popup = tk.Toplevel(self.root)
        editor_popup.title(f"Edit Item: {name}")
        editor_popup.transient(self.root)
        editor_popup.grab_set()
        editor_popup.geometry("600x400")
        from ui.item_editor import ItemEditor
        popup_item_editor = ItemEditor(
            editor_popup,
            on_save=self._on_save_item,
            on_delete=self._on_delete_item,
            on_cancel=editor_popup.destroy
        )
        popup_item_editor.pack(fill=tk.BOTH, expand=True)
        popup_item_editor.edit_item(name, item)

    def _on_save_item(self, name, item):
        if name:
            success = self.item_service.update_item(name, item)
        else:
            success = self.item_service.add_item(item)
        if success:
            self.show_optimal_items()
        return success

    def _on_delete_item(self, name):
        success = self.item_service.delete_item(name)
        if success:
            self.show_optimal_items()
        return success

    def reset_optimal(self):
        self.optimal_items = None
        self.show_optimal_items()

    def _on_window_focus_in(self, event):
        # Only focus if the event is for the main menu window itself
        if event.widget == self.root:
            self.budget_entry.focus_set()

    def update_output_weights_table(self):
        """Update the output weights table with current values"""
        print("Updating output weights table...")
        # Clear existing items
        for item in self.output_weights_tree.get_children():
            self.output_weights_tree.delete(item)
            
        # Add current output weights
        sorted_weights = sorted(self.item_service.output_weights.items())
        print(f"Current output weights: {dict(sorted_weights)}")
        for weight_name, value in sorted_weights:
            # Format the value to 2 decimal places
            formatted_value = f"{value:.2f}"
            self.output_weights_tree.insert("", tk.END, values=(weight_name, formatted_value))
        print("Finished updating output weights table")

    def calculate_weights(self):
        """Manually trigger weight calculation and update the output weights"""
        # Visual feedback that calculation is happening
        original_bg = self.calc_weights_btn.cget("bg")
        original_text = self.calc_weights_btn.cget("text")
        self.calc_weights_btn.config(bg='#00e676', text="Calculating...")
        self.root.update_idletasks()  # Force UI update
        
        try:
            # Do the calculation
            self.item_service.calculate_and_apply_output_weights()
            
            # Update the output weights table first
            self.update_output_weights_table()
            
            # Then update display if items are shown
            if self.optimal_items:
                self.show_optimal_items()
                
            # Save the changes
            self.item_service.save_data()
                
        finally:
            # Reset button appearance after a short delay
            self.root.after(500, lambda: self.calc_weights_btn.config(
                bg=original_bg, text=original_text))

    def run(self):
        self.root.mainloop()

# The SearchWindow will be created in the next step. 