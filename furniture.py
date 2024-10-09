import json
import os
import uuid  # Import the uuid module to generate unique IDs

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

def add_furniture_with_sale(furniture_list, name, original_price,  room, url, sale_price=None):
    """Add a furniture item with its sale price, original price, and URL to the list."""
    furniture_item = {
        'id': str(uuid.uuid4()),  # Generate a unique ID for each item
        'name': name,
        'original_price': original_price,
        'sale_price': sale_price if sale_price else None,  # Ensure sale_price is None if not on sale
        'room': room,
        'url': url}
    furniture_list.append(furniture_item)
    save_furniture_list(furniture_list)



def remove_furniture(furniture_list, furniture_id):
    """Remove a furniture item by its unique ID."""
    updated_list = [item for item in furniture_list if item['id'] != furniture_id]
    if len(updated_list) != len(furniture_list):
        save_furniture_list(updated_list)
        return True  # Indicates that an item was removed
    return False  # No item with that ID was found

def update_furniture(furniture_list, furniture_id, new_original_price=None, new_sale_price=None, new_room=None, new_url=None):
    """Update a furniture item's details by ID."""
    updated = False
    for item in furniture_list:
        if item['id'] == furniture_id:
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
    return False  # No item with that ID was found
