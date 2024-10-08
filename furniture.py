import json
import os

FURNITURE_FILE = os.path.join(os.path.dirname(__file__), 'data/furniture_list.json')

def load_furniture_list():
    """Load the furniture list from the JSON file."""
    if not os.path.exists(FURNITURE_FILE):
        with open(FURNITURE_FILE, 'w') as file:
            json.dump([], file)

    with open(FURNITURE_FILE, 'r') as file:
        return json.load(file)

def save_furniture_list(furniture_list):
    """Save the furniture list to the JSON file."""
    with open(FURNITURE_FILE, 'w') as file:
        json.dump(furniture_list, file, indent=4)

def add_furniture_with_sale(furniture_list, name, original_price, sale_price, room, url):
    """Add a furniture item with its sale price, original price, and URL to the list."""
    furniture_item = {
        'name': name,
        'original_price': original_price,
        'sale_price': sale_price,
        'room': room,
        'url': url
    }
    furniture_list.append(furniture_item)
    save_furniture_list(furniture_list)

def remove_furniture(furniture_list, name):
    """Remove a furniture item by name."""
    updated_list = [item for item in furniture_list if item['name'].lower() != name.lower()]
    if len(updated_list) != len(furniture_list):
        save_furniture_list(updated_list)
        return True  # Indicates that an item was removed
    return False  # No item with that name was found

def update_furniture(furniture_list, name, new_original_price=None, new_sale_price=None, new_room=None, new_url=None):
    """Update a furniture item's details by name."""
    updated = False
    for item in furniture_list:
        if item['name'].lower() == name.lower():
            if new_original_price is not None:
                item['original_price'] = new_original_price
            if new_sale_price is not None:
                item['sale_price'] = new_sale_price
            if new_room is not None:
                item['room'] = new_room
            if new_url is not None:
                item['url'] = new_url
            updated = True
            break
    if updated:
        save_furniture_list(furniture_list)
        return True  # Indicates the item was updated
    return False  # No item with that name was found
