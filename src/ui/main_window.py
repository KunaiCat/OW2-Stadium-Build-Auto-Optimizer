"""Main window component for the application."""
import tkinter as tk
from typing import List
from models.category import Category
from services.item_service import ItemService
from services.optimizer import OptimizerService
from ui.search_bar import SearchBar
from ui.item_list import ItemList
from ui.item_editor import ItemEditor
from ui.weight_sidebar import WeightSidebar
from utils.constants import UIConstant

class MainWindow:
    """Main window of the application."""

    def __init__(self, item_service: ItemService, optimizer_service: OptimizerService):
        """Initialize the main window.
        
        Args:
            item_service: Service for managing items
            optimizer_service: Service for finding optimal items
        """
        self.item_service = item_service
        self.optimizer_service = optimizer_service
        
        # Create root window
        self.root = tk.Tk()
        self.root.title("Item Manager")
        self.root.geometry("1024x800")
        self.root.minsize(UIConstant.MIN_WINDOW_WIDTH, UIConstant.MIN_WINDOW_HEIGHT)
        
        # Hide weights variable
        self.hide_weights = tk.BooleanVar(value=False)
        self.hide_weights.trace('w', self._on_hide_weights_change)
        
        # Track application focus
        self.app_has_focus = False
        self.root.bind("<FocusIn>", self._on_window_focus_in)
        self.root.bind("<FocusOut>", self._on_window_focus_out)
        
        # Track window size
        self.root.bind('<Configure>', self._on_window_resize)
        
        self._setup_ui()
        self._refresh_display()

    def _setup_ui(self):
        """Set up the UI components."""
        # Main container
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Top bar frame for edit mode toggle
        top_bar = tk.Frame(self.container)
        top_bar.pack(fill=tk.X, padx=2, pady=1)
        
        # Hide weights toggle in top right
        tk.Checkbutton(top_bar, text="Hide Weights", 
                      variable=self.hide_weights).pack(side=tk.RIGHT)
        
        # Main content area (on left)
        self.main_frame = tk.Frame(self.container)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Search bar
        self.search_bar = SearchBar(
            self.main_frame,
            on_search_change=self._on_search_change,
            on_optimize=self._on_optimize,
            on_reset=self._on_reset
        )
        self.search_bar.pack(fill=tk.X)
        
        # Item list
        self.item_list = ItemList(
            self.main_frame,
            on_edit=self._on_edit_item
        )
        self.item_list.pack(fill=tk.BOTH, expand=True)
        
        # Item editor (hidden by default)
        self.item_editor = ItemEditor(
            self.main_frame,
            on_save=self._on_save_item,
            on_delete=self._on_delete_item,
            on_cancel=self._on_cancel_edit
        )
        
        # Sidebar for weights (on right)
        self.sidebar = WeightSidebar(
            self.container,
            on_weight_change=self._on_weight_change
        )
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
        
        # Initialize weights
        for field, value in self.item_service.weights.items():
            self.sidebar.set_weight(field, value)

    def _refresh_display(self):
        """Refresh the item display."""
        # Get current search text and categories
        search_text = self.search_bar.search_var.get().strip()
        
        categories = []
        if self.search_bar.show_weapon.get():
            categories.append(Category.WEAPON)
        if self.search_bar.show_ability.get():
            categories.append(Category.ABILITY)
        if self.search_bar.show_survival.get():
            categories.append(Category.SURVIVAL)
        
        # Get filtered items
        items = self.item_service.get_filtered_items(search_text, categories)
        
        # Update display
        self.item_list.display_items(items)

    def _on_search_change(self, search_text: str, categories: List[Category]):
        """Handle changes to search criteria."""
        self._refresh_display()

    def _on_optimize(self, budget: int):
        """Handle optimization request."""
        # Find optimal items
        optimal_items, _, _ = self.optimizer_service.find_optimal_items(
            budget, self.item_service.items)
        
        # Update item list
        self.item_list.set_optimal_items(optimal_items)
        self._refresh_display()

    def _on_reset(self):
        """Handle reset request."""
        self.item_list.set_optimal_items(None)
        self._refresh_display()

    def _on_edit_item(self, name: str):
        """Handle edit item request."""
        item = self.item_service.get_item(name)
        if item:
            # Open item editor in a popup window
            self._open_item_editor_popup(name, item)

    def _on_save_item(self, name: str, item) -> bool:
        """Handle save item request."""
        if name:
            success = self.item_service.update_item(name, item)
        else:
            success = self.item_service.add_item(item)
            
        if success:
            self._refresh_display()
        return success

    def _on_delete_item(self, name: str) -> bool:
        """Handle delete item request."""
        success = self.item_service.delete_item(name)
        if success:
            self._refresh_display()
        return success

    def _on_cancel_edit(self):
        """Handle cancel edit request."""
        if hasattr(self, 'editor_popup') and self.editor_popup:
            self.editor_popup.destroy()
            self.editor_popup = None
        self._refresh_display()

    def _on_weight_change(self, field: str, value: float):
        """Handle weight value change."""
        self.item_service.update_weight(field, value)
        self._refresh_display()

    def _on_hide_weights_change(self, *args):
        """Handle hide weights toggle."""
        if self.hide_weights.get():
            self.sidebar.pack_forget()
            self.main_frame.pack_configure(padx=(4, 0))
        else:
            self.main_frame.pack_configure(padx=4)
            self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
        
        # Force a redraw
        self.root.update_idletasks()
        self._refresh_display()

    def _on_window_resize(self, event):
        """Handle window resize events."""
        if event.widget == self.root:
            self.item_list.update_columns(event.width)

    def _on_window_focus_in(self, event):
        """Handle window receiving focus."""
        if not self.app_has_focus and event.widget == self.root:
            self.search_bar.focus_search()
        self.app_has_focus = True
    
    def _on_window_focus_out(self, event):
        """Handle window losing focus."""
        if event.widget == self.root:
            self.app_has_focus = False

    def run(self):
        """Start the application."""
        self.root.mainloop()

    # Add a new method for popup editing
    def _open_item_editor_popup(self, name, item):
        self.editor_popup = tk.Toplevel(self.root)
        self.editor_popup.title(f"Edit Item: {name}")
        self.editor_popup.transient(self.root)
        self.editor_popup.grab_set()
        self.editor_popup.geometry("600x400")
        # Place the item editor in the popup
        self.popup_item_editor = ItemEditor(
            self.editor_popup,
            on_save=self._on_save_item,
            on_delete=self._on_delete_item,
            on_cancel=self._on_cancel_edit
        )
        self.popup_item_editor.pack(fill=tk.BOTH, expand=True)
        self.popup_item_editor.edit_item(name, item)

class SearchWindow:
    """Search window of the application (no sidebar)."""

    def __init__(self, parent, item_service: ItemService, optimizer_service: OptimizerService):
        self.item_service = item_service
        self.optimizer_service = optimizer_service
        self.root = parent
        self.root.title("Search")
        self.root.geometry("1024x800")
        self.root.minsize(UIConstant.MIN_WINDOW_WIDTH, UIConstant.MIN_WINDOW_HEIGHT)

        # Track application focus
        self.app_has_focus = False
        self.root.bind("<FocusIn>", self._on_window_focus_in)
        self.root.bind("<FocusOut>", self._on_window_focus_out)
        self.root.bind('<Configure>', self._on_window_resize)

        self._setup_ui()
        self._refresh_display()

    def _setup_ui(self):
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Top bar (no hide weights toggle)
        top_bar = tk.Frame(self.container)
        top_bar.pack(fill=tk.X, padx=2, pady=1)

        # Main content area
        self.main_frame = tk.Frame(self.container)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.search_bar = SearchBar(
            self.main_frame,
            on_search_change=self._on_search_change,
            on_optimize=self._on_optimize,
            on_reset=self._on_reset
        )
        self.search_bar.pack(fill=tk.X)

        self.item_list = ItemList(
            self.main_frame,
            on_edit=self._on_edit_item
        )
        self.item_list.pack(fill=tk.BOTH, expand=True)

        self.item_editor = ItemEditor(
            self.main_frame,
            on_save=self._on_save_item,
            on_delete=self._on_delete_item,
            on_cancel=self._on_cancel_edit
        )

    def _refresh_display(self):
        """Refresh the item display."""
        # Get current search text and categories
        search_text = self.search_bar.search_var.get().strip()
        
        categories = []
        if self.search_bar.show_weapon.get():
            categories.append(Category.WEAPON)
        if self.search_bar.show_ability.get():
            categories.append(Category.ABILITY)
        if self.search_bar.show_survival.get():
            categories.append(Category.SURVIVAL)
        
        # Get filtered items
        items = self.item_service.get_filtered_items(search_text, categories)
        
        # Update display
        self.item_list.display_items(items)

    def _on_search_change(self, search_text: str, categories: List[Category]):
        """Handle changes to search criteria."""
        self._refresh_display()

    def _on_optimize(self, budget: int):
        """Handle optimization request."""
        # Find optimal items
        optimal_items, _, _ = self.optimizer_service.find_optimal_items(
            budget, self.item_service.items)
        
        # Update item list
        self.item_list.set_optimal_items(optimal_items)
        self._refresh_display()

    def _on_reset(self):
        """Handle reset request."""
        self.item_list.set_optimal_items(None)
        self._refresh_display()

    def _on_edit_item(self, name: str):
        """Handle edit item request."""
        item = self.item_service.get_item(name)
        if item:
            # Open item editor in a popup window
            self._open_item_editor_popup(name, item)

    def _on_save_item(self, name: str, item) -> bool:
        """Handle save item request."""
        if name:
            success = self.item_service.update_item(name, item)
        else:
            success = self.item_service.add_item(item)
            
        if success:
            self._refresh_display()
        return success

    def _on_delete_item(self, name: str) -> bool:
        """Handle delete item request."""
        success = self.item_service.delete_item(name)
        if success:
            self._refresh_display()
        return success

    def _on_cancel_edit(self):
        """Handle cancel edit request."""
        if hasattr(self, 'editor_popup') and self.editor_popup:
            self.editor_popup.destroy()
            self.editor_popup = None
        self._refresh_display()

    def _on_window_resize(self, event):
        """Handle window resize events."""
        if event.widget == self.root:
            self.item_list.update_columns(event.width)

    def _on_window_focus_in(self, event):
        """Handle window receiving focus."""
        if not self.app_has_focus and event.widget == self.root:
            self.search_bar.focus_search()
        self.app_has_focus = True
    
    def _on_window_focus_out(self, event):
        """Handle window losing focus."""
        if event.widget == self.root:
            self.app_has_focus = False

    # Add a new method for popup editing
    def _open_item_editor_popup(self, name, item):
        self.editor_popup = tk.Toplevel(self.root)
        self.editor_popup.title(f"Edit Item: {name}")
        self.editor_popup.transient(self.root)
        self.editor_popup.grab_set()
        self.editor_popup.geometry("600x400")
        # Place the item editor in the popup
        self.popup_item_editor = ItemEditor(
            self.editor_popup,
            on_save=self._on_save_item,
            on_delete=self._on_delete_item,
            on_cancel=self._on_cancel_edit
        )
        self.popup_item_editor.pack(fill=tk.BOTH, expand=True)
        self.popup_item_editor.edit_item(name, item) 