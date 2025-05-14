"""Service for finding optimal item combinations."""
from typing import Dict, List, Tuple
from models.item import Item
from utils.constants import MAX_ITEMS

class OptimizerService:
    """Service for finding optimal item combinations within a budget."""

    @staticmethod
    def find_optimal_items(budget: int, items: Dict[str, Item]) -> Tuple[List[str], int, float]:
        """Find the optimal combination of items within the given budget.
        
        Args:
            budget: Maximum total price
            items: Dictionary of available items
            
        Returns:
            Tuple containing:
            - List of selected item names
            - Total price of selected items
            - Total weight of selected items
        """
        # Convert items to list and sort by weight per 1000 price (efficiency)
        items_list = [(name, item.price, item.total_weight) 
                     for name, item in items.items()]
        items_list.sort(key=lambda x: x[2]/x[1], reverse=True)
        
        # Track best combination found
        best_combination = []
        best_weight = 0
        best_price = 0
        
        def backtrack(start_idx: int, current_items: List[str], 
                     current_price: int, current_weight: float) -> None:
            """Recursive backtracking to find optimal combination.
            
            Args:
                start_idx: Starting index in sorted items list
                current_items: Currently selected items
                current_price: Total price of current selection
                current_weight: Total weight of current selection
            """
            nonlocal best_combination, best_weight, best_price
            
            # Update best if current is better
            if current_weight > best_weight and current_price <= budget:
                best_combination = current_items.copy()
                best_weight = current_weight
                best_price = current_price
            
            # Stop if we've reached the end or max items
            if start_idx >= len(items_list) or len(current_items) >= MAX_ITEMS:
                return
            
            # Try adding each remaining item
            for i in range(start_idx, len(items_list)):
                item_name, item_price, item_weight = items_list[i]
                
                # Skip if adding this item would exceed budget
                if current_price + item_price > budget:
                    continue
                
                # Try this item
                current_items.append(item_name)
                backtrack(i + 1, current_items, 
                         current_price + item_price, 
                         current_weight + item_weight)
                current_items.pop()
        
        # Start the backtracking search
        backtrack(0, [], 0, 0)
        
        return best_combination, best_price, best_weight 