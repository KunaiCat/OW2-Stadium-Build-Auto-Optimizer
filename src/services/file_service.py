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

    def load_data(self) -> Tuple[Dict, Dict]:
        """Load items and weights from the JSON file.
        
        Returns:
            Tuple containing (items_dict, weights_dict)
        """
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    if (
                        isinstance(data, dict)
                        and 'items' in data
                        and 'weights' in data
                    ):
                        return data['items'], data['weights']
                    else:
                        # Old format migration
                        weights = self._create_default_weights()
                        return data, weights
            else:
                return {}, self._create_default_weights()
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}, self._create_default_weights()

    def save_data(self, items: Dict, weights: Dict) -> bool:
        """Save items and weights to the JSON file.
        
        Args:
            items: Dictionary of items
            weights: Dictionary of weights
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            data = {
                'items': items,
                'weights': weights
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