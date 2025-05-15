import sys
import os
import pytest

# Adjust path for local imports if running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from services.optimizer import OptimizerService
from models.item import Item

def test_empty_items():
    result = OptimizerService.find_optimal_items(1000, {})
    assert result == ([], 0, 0), f"Expected empty result, got {result}"

def test_single_item_under_budget():
    items = {"A": Item("A", 500, total_weight=10)}
    result = OptimizerService.find_optimal_items(1000, items)
    assert set(result[0]) == {"A"}
    assert result[1] == 500
    assert abs(result[2] - 10) < 1e-6

def test_single_item_over_budget():
    items = {"A": Item("A", 1500, total_weight=10)}
    result = OptimizerService.find_optimal_items(1000, items)
    assert result == ([], 0, 0)

def test_two_items_fit():
    items = {
        "A": Item("A", 500, total_weight=10),
        "B": Item("B", 400, total_weight=20)
    }
    result = OptimizerService.find_optimal_items(1000, items)
    assert set(result[0]) == {"A", "B"}
    assert result[1] == 900
    assert abs(result[2] - 30) < 1e-6

def test_two_items_only_one_fits():
    items = {
        "A": Item("A", 800, total_weight=10),
        "B": Item("B", 900, total_weight=20)
    }
    result = OptimizerService.find_optimal_items(1000, items)
    # Only one can fit, should pick the one with higher weight
    assert (set(result[0]) == {"B"} and result[1] == 900) or (set(result[0]) == {"A"} and result[1] == 800)
    assert result[2] in (10, 20)

def test_max_items_limit():
    items = {chr(65+i): Item(chr(65+i), 100, total_weight=10+i) for i in range(10)}
    result = OptimizerService.find_optimal_items(1000, items)
    # Should not select more than 6 items (default MAX_ITEMS is 6)
    assert len(result[0]) <= 6
    assert result[1] <= 1000

def test_realistic_case():
    from services.item_service import ItemService
    from services.file_service import FileService
    item_service = ItemService(FileService())
    items = dict(list(item_service.items.items())[:10])  # First 10 items
    result = OptimizerService.find_optimal_items(5000, items)
    # Should not exceed budget
    assert result[1] <= 5000
    # Should not select more than 6 items
    assert len(result[0]) <= 6

# You can add more edge cases as needed!