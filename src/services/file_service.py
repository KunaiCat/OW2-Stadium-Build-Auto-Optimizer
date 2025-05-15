"""Service for handling file operations."""
import json
from typing import Dict, Tuple
from pathlib import Path
import os

class FileService:
    """Handles loading and saving data from/to JSON files."""
    
    def __init__(self, file_path: str = None):
        """Initialize the file service with the path to the items file."""
        if file_path is None:
            # Always use the items.json in the repo root
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(repo_root, "items.json")
        self.file_path = Path(file_path)

    def load_data(self) -> Tuple[Dict, Dict, Dict]:
        """Load items and weights from the JSON file.
        
        Returns:
            Tuple containing (items_dict, weights_dict, output_weights)
        """
        if not os.path.exists(self.file_path):
            base_weights = self._create_default_weights()
            return {}, {"Base Weights": base_weights}, base_weights.copy()
            
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            items = data.get('items', {})
            weights = data.get('weights', {})
            output_weights = data.get('output_weights', {})
            
            # Handle legacy format conversion
            if not weights:
                # If weights is empty, create default
                weights = {"Base Weights": self._create_default_weights()}
            elif 'Base Weights' not in weights:
                # If weights exists but doesn't have Base Weights, wrap it
                weights = {"Base Weights": weights}
                
            # If no output weights, initialize with base weights
            if not output_weights:
                output_weights = weights.get("Base Weights", {}).copy()
                
            return items, weights, output_weights
            
        except Exception as e:
            print(f"Error loading data: {e}")
            base_weights = self._create_default_weights()
            return {}, {"Base Weights": base_weights}, base_weights.copy()

    def save_data(self, items: Dict, weights: Dict, output_weights: Dict) -> bool:
        """Save items and weights to the JSON file.
        
        Args:
            items: Dictionary of items
            weights: Dictionary of weight profiles
            output_weights: Dictionary of calculated output weights
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            data = {
                'items': items,
                'weights': weights,
                'output_weights': output_weights
            }
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def _create_default_weights(self) -> Dict[str, float]:
        """Create default weights dictionary."""
        weights = {
            'Adjustment': 1.0,
            'Effect Value': 1.0,
            'Weapon Power': 1.0,
            'Weapon Lifesteal': 1.0,
            'Attack Speed': 1.0,
            'Reload Speed': 1.0,
            'Move Speed': 1.0,
            'Critical Damage': 1.0,
            'Melee Damage': 1.0,
            'Max Ammo': 1.0,
            'Cooldown Reduction': 1.0,
            'Ability Power': 1.0,
            'Ability Lifesteal': 1.0,
            'Armor': 1.0,
            'Shields': 1.0,
            'Health': 1.0
        }
        return weights 