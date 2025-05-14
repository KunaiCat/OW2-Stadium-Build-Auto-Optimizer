import json


def find_optimal_items(budget, items_dict):
    items_list = [(name, data['Price'], data['Total Weight']) for name, data in items_dict.items()]
    items_list.sort(key=lambda x: x[2]/x[1], reverse=True)
    best_combination = []
    best_weight = 0
    best_price = 0
    def backtrack(start_idx, current_items, current_price, current_weight):
        nonlocal best_combination, best_weight, best_price
        if current_weight > best_weight and current_price <= budget:
            best_combination = current_items.copy()
            best_weight = current_weight
            best_price = current_price
        if start_idx >= len(items_list) or len(current_items) >= 6:
            return
        for i in range(start_idx, len(items_list)):
            item_name, item_price, item_weight = items_list[i]
            if current_price + item_price > budget:
                continue
            current_items.append(item_name)
            backtrack(i + 1, current_items, current_price + item_price, current_weight + item_weight)
            current_items.pop()
    backtrack(0, [], 0, 0)
    return best_combination, best_price, best_weight


if __name__ == "__main__":
    with open('items.json', 'r') as f:
        items = json.load(f)
    new_items = {}
    for key, value in items.items():
        new_entry = {
            'price':value['Price'],
            'base_weight':value['Total Weight']
        }
        new_items[key] = new_entry
    with open('items.json', 'w') as f:
        json.dump(new_items, f, indent=2)
    input('sus...')
    while True:
        budget = int(input('Enter budget\n'))
        selected, total_price, total_weight = find_optimal_items(budget, items)
    
        print(f"Selected items: {selected}")
        print(f"Total price: {total_price}")
        print(f"Total weight: {total_weight}")
