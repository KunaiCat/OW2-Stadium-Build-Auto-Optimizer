"""Service for managing the collection of items."""
from typing import Dict, List, Optional, Set
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
        self.weights: Dict[str, Dict[str, float]] = {}
        self.output_weights: Dict[str, float] = {}
        self.enabled_profiles: Set[str] = {"Base Weights"}  # Base Weights is always enabled
        self._load_data()
        # Don't automatically calculate output weights on startup

    def _load_data(self) -> None:
        """Load items and weights from file."""
        items_dict, weights_dict, output_weights = self.file_service.load_data()
        self.weights = weights_dict
        self.output_weights = output_weights
        
        # Convert dictionary items to Item objects
        self.items = {
            name: Item.from_dict(name, data)
            for name, data in items_dict.items()
        }
        
        # Initialize enabled profiles and ensure profiles have required fields
        self.enabled_profiles = {"Base Weights"}  # Base Weights is always enabled
        for profile_name, profile in self.weights.items():
            # Ensure all profiles have required fields
            if profile_name != "Base Weights":
                # Set default values if missing
                if "_min" not in profile:
                    profile["_min"] = 0.1
                if "_max" not in profile:
                    profile["_max"] = 2.0
                if "_scale" not in profile:
                    profile["_scale"] = 0.5
                
                # Check if profile is enabled
                if profile.get("_enabled", True):
                    self.enabled_profiles.add(profile_name)
        
        # Calculate weights for all items
        self._calculate_output_weights()
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
        
        # Mark profiles as enabled/disabled
        for profile in self.weights:
            if profile != "Base Weights":
                self.weights[profile]["_enabled"] = profile in self.enabled_profiles
        
        return self.file_service.save_data(items_dict, self.weights, self.output_weights)

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
        item.calculate_total_weight(self.output_weights)
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
        updated_item.calculate_total_weight(self.output_weights)
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

    def get_filtered_items(
        self,
        search_text: str = "",
        categories: Optional[List[Category]] = None
    ) -> Dict[str, Item]:
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

    def update_weight(self, field: str, value: float, recalculate: bool = False) -> None:
        """Update a base weight value and recalculate all items.
        
        Args:
            field: Name of the weight field to update
            value: New weight value
            recalculate: Whether to recalculate output weights (default False)
        """
        self.weights["Base Weights"][field] = value
        if recalculate:
            self._calculate_output_weights()
            self.recalculate_weights()
        self.save_data()
        
    def add_or_update_weight_profile(self, profile_name: str, weights: Dict[str, float], recalculate: bool = False) -> None:
        """Add or update a custom weight profile.
        
        Args:
            profile_name: Name of the weight profile
            weights: Dictionary of weight values
            recalculate: Whether to recalculate output weights (default False)
        """
        is_new = profile_name not in self.weights
        self.weights[profile_name] = weights
        
        # Enable new profiles by default
        if is_new:
            self.enabled_profiles.add(profile_name)
            weights["_enabled"] = True
        else:
            weights["_enabled"] = profile_name in self.enabled_profiles
            
        if recalculate:
            self._calculate_output_weights()
            self.recalculate_weights()
        self.save_data()
        
    def delete_weight_profile(self, profile_name: str, recalculate: bool = False) -> bool:
        """Delete a custom weight profile.
        
        Args:
            profile_name: Name of the weight profile to delete
            recalculate: Whether to recalculate output weights (default False)
            
        Returns:
            bool: True if profile was deleted
        """
        if profile_name == "Base Weights":
            return False  # Cannot delete base weights
            
        if profile_name in self.weights:
            del self.weights[profile_name]
            if profile_name in self.enabled_profiles:
                self.enabled_profiles.remove(profile_name)
            
            if recalculate:
                self._calculate_output_weights()
                self.recalculate_weights()
            self.save_data()
            return True
        return False
        
    def toggle_weight_profile(self, profile_name: str, enabled: bool, recalculate: bool = False) -> None:
        """Toggle a weight profile on/off.
        
        Args:
            profile_name: Name of the weight profile
            enabled: True to enable, False to disable
            recalculate: Whether to recalculate output weights (default False)
        """
        if profile_name == "Base Weights":
            return  # Base weights are always enabled
            
        if profile_name in self.weights:
            if enabled and profile_name not in self.enabled_profiles:
                self.enabled_profiles.add(profile_name)
                self.weights[profile_name]["_enabled"] = True
                if recalculate:
                    self._calculate_output_weights()
                    self.recalculate_weights()
                self.save_data()
            elif not enabled and profile_name in self.enabled_profiles:
                self.enabled_profiles.remove(profile_name)
                self.weights[profile_name]["_enabled"] = False
                if recalculate:
                    self._calculate_output_weights()
                    self.recalculate_weights()
                self.save_data()
                
    def calculate_and_apply_output_weights(self) -> None:
        """Manually calculate and apply output weights based on enabled profiles."""
        # Calculate new output weights
        self._calculate_output_weights()
        
        # Only recalculate item weights if output weights actually changed
        old_weights = self.output_weights.copy()
        if old_weights != self.output_weights:
            self.recalculate_weights()
            
        # Save changes to both weights and output_weights
        self.save_data()
                
    def _calculate_output_weights(self) -> None:
        """Calculate output weights by combining all enabled weight profiles."""
        print("Starting output weights calculation...")
        # Start with default values for all keys
        all_keys = set()
        for profile_name, weights in self.weights.items():
            all_keys.update(k for k in weights.keys() if not k.startswith("_"))
            
        # Start with a weight of 1.0 for all fields
        output = {key: 1.0 for key in all_keys}
        print(f"Initial output weights: {output}")
        
        # Process Base Weights first (always enabled and not scaled)
        if "Base Weights" in self.weights:
            base_profile = self.weights["Base Weights"]
            for key in all_keys:
                if key in base_profile and not key.startswith("_"):
                    output[key] *= base_profile[key]
            print(f"After applying Base Weights: {output}")
        
        # Process other enabled profiles with scaling
        for profile_name, profile in self.weights.items():
            if profile_name == "Base Weights":
                continue  # Already processed
                
            # Skip disabled profiles - check both the _enabled flag and enabled_profiles set
            if not profile.get("_enabled", False) or profile_name not in self.enabled_profiles:
                print(f"Skipping disabled profile {profile_name}")
                continue
                
            print(f"Processing enabled profile {profile_name}")
            
            # Get min, max, and scale values with defaults if not present
            min_val = profile.get("_min", 0.1)
            max_val = profile.get("_max", 2.0)
            scale_percent = profile.get("_scale", 0.5)
            
            # Calculate scale factor using linear interpolation
            scale_factor = min_val + scale_percent * (max_val - min_val)
            print(f"Processing profile {profile_name} with scale factor {scale_factor}")
            
            # Apply scaled weights (only if the weight is not 1.0)
            for key in all_keys:
                if key in profile and not key.startswith("_"):
                    weight_value = profile[key]
                    # Only scale if not 1.0
                    if weight_value != 1.0:
                        scaled_value = weight_value * scale_factor
                        output[key] *= scaled_value
            print(f"After applying {profile_name}: {output}")
        
        print(f"Final output weights: {output}")
        self.output_weights = output

    def recalculate_weights(self) -> None:
        """Recalculate weights for all items using the output weights."""
        for item in self.items.values():
            item.calculate_total_weight(self.output_weights) 