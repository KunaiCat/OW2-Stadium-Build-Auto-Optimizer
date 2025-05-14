import tkinter as tk
from ui.weight_sidebar import WeightSidebar
from ui.main_window import SearchWindow
from ui.item_list import ItemList
from services.item_service import ItemService
from services.optimizer import OptimizerService

class MainMenu:
    def __init__(self, item_service: ItemService, optimizer_service: OptimizerService):
        self.root = tk.Tk()
        self.root.title("Main Menu")
        self.root.geometry("900x700")
        self.item_service = item_service
        self.optimizer_service = optimizer_service
        self.optimal_items = None

        tk.Label(self.root, text="Select a window to open:", font=("Arial", 12)).pack(pady=20)
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Search", width=12, command=self.open_search).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Weights", width=12, command=self.open_weights).pack(side=tk.LEFT, padx=10)

        # Budget entry and Find Items button
        budget_frame = tk.Frame(self.root)
        budget_frame.pack(pady=20)
        tk.Label(budget_frame, text="Budget:").pack(side=tk.LEFT, padx=(0, 5))
        self.budget_var = tk.StringVar()
        self.budget_entry = tk.Entry(budget_frame, textvariable=self.budget_var, width=12)
        self.budget_entry.pack(side=tk.LEFT)
        tk.Button(budget_frame, text="Find Items", command=self.find_items).pack(side=tk.LEFT, padx=10)
        self.budget_error = tk.Label(self.root, text="", fg="red", font=("Arial", 10))
        self.budget_error.pack()
        self.budget_entry.bind('<Key>', self.clear_budget_error)

        # Container for reset button and item cards
        self.cards_container = tk.Frame(self.root)
        self.cards_container.pack(fill=tk.BOTH, expand=True)

        self.reset_btn = None
        self.item_list = None

    def open_search(self):
        win = tk.Toplevel(self.root)
        win.title("Search")
        win.geometry("1024x800")
        SearchWindow(win, self.item_service, self.optimizer_service)

    def open_weights(self):
        win = tk.Toplevel(self.root)
        win.title("Weights")
        win.geometry("300x600")
        sidebar = WeightSidebar(win, on_weight_change=self.item_service.update_weight)
        sidebar.pack(fill=tk.BOTH, expand=True)
        for field, value in self.item_service.weights.items():
            sidebar.set_weight(field, value)

    def find_items(self):
        budget_str = self.budget_var.get().strip()
        try:
            budget = int(budget_str)
            if budget < 3500:
                raise ValueError
        except ValueError:
            self.flash_budget_error()
            return
        self.clear_budget_error()
        optimal_items, _, _ = self.optimizer_service.find_optimal_items(budget, self.item_service.items)
        self.optimal_items = optimal_items
        self.show_optimal_items()

    def flash_budget_error(self):
        self.budget_entry.config(bg='#ffcccc')
        self.budget_error.config(text="Please enter an integer budget of at least 3500.")
        self.root.after(200, lambda: self.budget_entry.config(bg='white'))

    def clear_budget_error(self, event=None):
        self.budget_entry.config(bg='white')
        self.budget_error.config(text="")

    def show_optimal_items(self):
        # Clear previous widgets
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        if self.optimal_items:
            # Reset button
            self.reset_btn = tk.Button(self.cards_container, text="Reset", command=self.reset_optimal)
            self.reset_btn.pack(anchor="ne", pady=(0, 5), padx=10)
            # Item cards
            items = {name: self.item_service.get_item(name) for name in self.optimal_items}
            self.item_list = ItemList(self.cards_container, on_edit=lambda n: None)
            self.item_list.pack(fill=tk.BOTH, expand=True)
            self.item_list.display_items(items)
        else:
            self.reset_btn = None
            self.item_list = None

    def reset_optimal(self):
        self.optimal_items = None
        self.show_optimal_items()

    def run(self):
        self.root.mainloop()

# The SearchWindow will be created in the next step. 