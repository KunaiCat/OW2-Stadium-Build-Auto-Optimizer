"""Service for finding optimal item combinations."""


from typing import Dict, List, Tuple
from models.item import Item
from utils.constants import GameConstant


class OptimizerService:
    """Service for finding optimal item combinations within a budget."""

    @staticmethod
    def find_optimal_items(
        budget: int,
        items: Dict[str, Item]
    ) -> Tuple[List[str], int, float]:
        """Interface for finding the optimal combination of items within the given budget.
        This delegates to the actual implementation, which can be swapped for a faster version later.
        """
        return OptimizerService._find_optimal_items_backtrack(budget, items)

    @staticmethod
    def _find_optimal_items_backtrack(
        budget: int,
        items: Dict[str, Item]
    ) -> Tuple[List[str], int, float]:
        """Original backtracking implementation for finding optimal items."""
        print(f"Finding optimal items with budget {budget}")
        # Convert items to list and sort by weight per 1000 price (efficiency)
        items_list = [
            (name, item.price, item.total_weight)
            for name, item in items.items()
        ]
        items_list.sort(key=lambda x: x[2] / x[1], reverse=True)
        print(f"Sorted {len(items_list)} items by efficiency")

        # Track best combination found
        best_combination = []
        best_weight = 0
        best_price = 0

        def backtrack(
            start_idx: int,
            current_items: List[str],
            current_price: int,
            current_weight: float
        ) -> None:
            """Recursive backtracking to find optimal combination."""
            nonlocal best_combination, best_weight, best_price

            # Update best if current is better
            if current_weight > best_weight and current_price <= budget:
                best_combination = current_items.copy()
                best_weight = current_weight
                best_price = current_price
                print(f"Found better combination: {best_combination}")
                print(f"Weight: {best_weight}, Price: {best_price}")

            # Stop if we've reached the end or max items
            if (
                start_idx >= len(items_list)
                or len(current_items) >= GameConstant.MAX_ITEMS
            ):
                return

            # Try adding each remaining item
            for i in range(start_idx, len(items_list)):
                item_name, item_price, item_weight = items_list[i]

                # Skip if adding this item would exceed budget
                if current_price + item_price > budget:
                    continue

                # Try this item
                current_items.append(item_name)
                backtrack(
                    i + 1,
                    current_items,
                    current_price + item_price,
                    current_weight + item_weight
                )
                current_items.pop()

        # Start the backtracking search
        print("Starting backtracking search...")
        backtrack(0, [], 0, 0)
        print(f"Search complete. Found {len(best_combination)} items.")
        return best_combination, best_price, best_weight 