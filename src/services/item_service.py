"""Service for managing the collection of items."""
from typing import Dict, List, Optional
from models.item import Item
from models.category import Category
from services.file_service import FileService

class ItemService:
    """Service for managing the collection of items and their weights."""
    
    def __init__(self, file_service: FileService):
        """Initialize the item service.
        
        Args:
            file_service: Service for loading/saving items from/to file
        """
        self.file_service = file_service
        self.items: Dict[str, Item] = {}
        self.weights: Dict[str, float] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Load items and weights from file."""
        items_dict, weights_dict = self.file_service.load_data()
        self.weights = weights_dict
        
        # Convert dictionary items to Item objects
        self.items = {
            name: Item.from_dict(name, data)
            for name, data in items_dict.items()
        }
        
        # Calculate weights for all items
        self.recalculate_weights()

    def save_data(self) -> bool:
        """Save current items and weights to file.
        
        Returns:
            bool: True if save was successful
        """
        items_dict = {
            name: item.to_dict()
            for name, item in self.items.items()
        }
        return self.file_service.save_data(items_dict, self.weights)

    def get_item(self, name: str) -> Optional[Item]:
        """Get an item by name.
        
        Args:
            name: Name of the item to get
            
        Returns:
            Item if found, None otherwise
        """
        return self.items.get(name)

    def add_item(self, item: Item) -> bool:
        """Add a new item to the collection.
        
        Args:
            item: Item to add
            
        Returns:
            bool: True if item was added, False if name already exists
        """
        if item.name in self.items:
            return False
        
        self.items[item.name] = item
        item.calculate_total_weight(self.weights)
        self.save_data()
        return True

    def update_item(self, name: str, updated_item: Item) -> bool:
        """Update an existing item.
        
        Args:
            name: Name of item to update
            updated_item: New item data
            
        Returns:
            bool: True if update was successful
        """
        if name not in self.items:
            return False
        
        # Handle name changes
        if name != updated_item.name:
            if updated_item.name in self.items:
                return False
            del self.items[name]
        
        self.items[updated_item.name] = updated_item
        updated_item.calculate_total_weight(self.weights)
        self.save_data()
        return True

    def delete_item(self, name: str) -> bool:
        """Delete an item by name.
        
        Args:
            name: Name of item to delete
            
        Returns:
            bool: True if item was deleted
        """
        if name in self.items:
            del self.items[name]
            self.save_data()
            return True
        return False

    def get_filtered_items(self, 
                         search_text: str = "", 
                         categories: Optional[List[Category]] = None) -> Dict[str, Item]:
        """Get filtered items based on search text and categories.
        
        Args:
            search_text: Text to search for in item names
            categories: List of categories to include, or None for all
            
        Returns:
            Dictionary of filtered items
        """
        filtered = {}
        search_text = search_text.lower().strip()
        
        for name, item in self.items.items():
            # Skip if doesn't match search text
            if search_text and search_text not in name.lower():
                continue
            
            # Skip if category doesn't match
            if categories is not None and item.category not in categories:
                continue
            
            filtered[name] = item
        
        return filtered

    def update_weight(self, field: str, value: float) -> None:
        """Update a weight value and recalculate all items.
        
        Args:
            field: Name of the weight field to update
            value: New weight value
        """
        self.weights[field] = value
        self.recalculate_weights()
        self.save_data()

    def recalculate_weights(self) -> None:
        """Recalculate weights for all items."""
        for item in self.items.values():
            item.calculate_total_weight(self.weights) 