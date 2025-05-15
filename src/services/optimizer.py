"""Service for finding optimal item combinations."""

from typing import Dict, List, Tuple
from models.item import Item
from utils.constants import GameConstant

# Try to import the C++ extension
# This allows the module to still be imported if the C++ extension hasn't been built,
# though calling find_optimal_items would then raise an error or fallback.
try:
    import knapsack_optimizer_cpp
    HAS_CPP_OPTIMIZER = True
except ImportError:
    HAS_CPP_OPTIMIZER = False
    # You could print a warning here or log this event
    print("WARNING: C++ knapsack_optimizer_cpp module not found. Optimizer will be slower.")

class OptimizerService:
    """Service for finding optimal item combinations within a budget."""

    @staticmethod
    def find_optimal_items(
        budget: int,
        items: Dict[str, Item]
    ) -> Tuple[List[str], int, float]:
        """Interface for finding the optimal combination of items within the given budget.
        Delegates to the C++ implementation if available, otherwise falls back
        to the Python implementation (or raises an error).
        """
        if HAS_CPP_OPTIMIZER:
            # Prepare data for C++ function: List[Tuple[str, int, double]]
            items_data_for_cpp = [
                (name, item.price, item.total_weight)
                for name, item in items.items()
            ]
            max_items = GameConstant.MAX_ITEMS
            return knapsack_optimizer_cpp.solve_knapsack_cpp(budget, items_data_for_cpp, max_items)
        else:
            # Fallback to Python implementation or raise an error
            # For now, let's keep the fallback to the Python version
            print("Using pure Python optimizer as C++ version is not available.")
            return OptimizerService._find_optimal_items_backtrack(budget, items)

    @staticmethod
    def _find_optimal_items_backtrack(
        budget: int,
        items: Dict[str, Item]
    ) -> Tuple[List[str], int, float]:
        """Original backtracking implementation for finding optimal items (Python version)."""
        # Convert items to list and sort by weight per 1000 price (efficiency)
        items_list = [
            (name, item.price, item.total_weight)
            for name, item in items.items()
        ]
        # Handle division by zero for items with price 0
        items_list.sort(key=lambda x: (x[2] / x[1]) if x[1] != 0 else float('inf') if x[2] > 0 else 0, reverse=True)

        best_combination = []
        best_weight = 0.0
        best_price = 0

        current_items_stack = [] # Using a list as a stack

        def backtrack(
            start_idx: int,
            current_price: int,
            current_weight: float
        ) -> None:
            nonlocal best_combination, best_weight, best_price, current_items_stack

            if current_weight > best_weight and current_price <= budget:
                best_combination = list(current_items_stack) # Make a copy
                best_weight = current_weight
                best_price = current_price

            if start_idx >= len(items_list) or len(current_items_stack) >= GameConstant.MAX_ITEMS:
                return

            for i in range(start_idx, len(items_list)):
                item_name, item_price, item_total_weight = items_list[i]

                if current_price + item_price > budget:
                    continue

                current_items_stack.append(item_name)
                backtrack(
                    i + 1, 
                    current_price + item_price,
                    current_weight + item_total_weight
                )
                current_items_stack.pop()

        backtrack(0, 0, 0.0)
        return best_combination, best_price, best_weight 