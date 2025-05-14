from dataclasses import dataclass, field
from typing import Dict, Optional
from .category import Category

@dataclass
class Item:
    """Represents an item in the game with its properties and stats."""
    name: str
    price: int
    adjustment: int = 0
    effect_value: int = 0
    effects: str = ""
    favorite: bool = False
    category: Category = Category.NONE
    total_weight: float = 0.0
    weight_per_1k: float = 0.0
    stats: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, name: str, data: Dict) -> 'Item':
        """Create an Item instance from a dictionary representation."""
        stats = {}
        for key, value in data.items():
            if key not in ['Price', 'Adjustment', 'Effect Value', 'Effects', 
                          'Favorite', 'Category', 'Total Weight', 'weight_per_1k']:
                stats[key] = value

        return cls(
            name=name,
            price=data['Price'],
            adjustment=data.get('Adjustment', 0),
            effect_value=data.get('Effect Value', 0),
            effects=data.get('Effects', ''),
            favorite=data.get('Favorite', False),
            category=Category(data.get('Category', Category.NONE)),
            total_weight=data.get('Total Weight', 0.0),
            weight_per_1k=data.get('weight_per_1k', 0.0),
            stats=stats
        )

    def to_dict(self) -> Dict:
        """Convert the item to its dictionary representation."""
        data = {
            'Price': self.price,
            'Adjustment': self.adjustment,
            'Effect Value': self.effect_value,
            'Effects': self.effects,
            'Favorite': self.favorite,
            'Category': self.category.value,
            'Total Weight': self.total_weight,
            'weight_per_1k': self.weight_per_1k
        }
        
        # Add optional stats
        data.update(self.stats)
        
        return data

    def calculate_total_weight(self, weights: Dict[str, float]) -> None:
        """Calculate total weight based on provided weight values."""
        total = 0.0
        
        # Add weights for standard fields
        total += self.adjustment * weights.get('Adjustment', 1.0)
        total += self.effect_value * weights.get('Effect Value', 1.0)
        
        # Add weights for optional stats
        for stat, value in self.stats.items():
            if stat in weights:
                total += value * weights[stat]
        
        self.total_weight = round(total, 2)
        self.weight_per_1k = round((total * 1000) / self.price, 2) if self.price else 0 