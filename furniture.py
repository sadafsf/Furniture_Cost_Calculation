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

def add_furniture_with_details(furniture_list, name, original_price=None, sale_price=None, min_price=None, max_price=None, min_sale_price=None, max_sale_price=None, room=None, url=None, image_url=None):
    """Add a furniture item with either price range or individual prices."""
    
    furniture_item = {
        'id': str(uuid.uuid4()),  # Generate a unique ID for each item
        'name': name,
        'original_price': original_price if not min_price and not max_price else None,  # Use original_price only if no min/max
        'sale_price': sale_price if not min_sale_price and not max_sale_price else None,  # Use sale_price only if no min/max
        'min_price': min_price,  # Add min price if available
        'max_price': max_price,  # Add max price if available
        'min_sale_price': min_sale_price,  # Add min sale price if available
        'max_sale_price': max_sale_price,  # Add max sale price if available
        'room': room,
        'url': url,
        'image_url': image_url if image_url else None  # Default to None if no image URL provided
    }
    
    furniture_list.append(furniture_item)
    save_furniture_list(furniture_list)



def remove_furniture(furniture_list, furniture_id):
    """Remove a furniture item by its unique ID."""
    updated_list = [item for item in furniture_list if item['id'] != furniture_id]
    if len(updated_list) != len(furniture_list):
        save_furniture_list(updated_list)
        return True  # Indicates that an item was removed
    return False  # No item with that ID was found

def update_furniture(furniture_list, furniture_id, new_original_price=None, new_sale_price=None, new_min_price=None, new_max_price=None, new_min_sale_price=None, new_max_sale_price=None, new_room=None, new_url=None, new_image_url=None):
    """Update a furniture item's details by ID, handling price ranges and individual prices."""
    updated = False
    for item in furniture_list:
        if item['id'] == furniture_id:
            if new_original_price is not None:
                item['original_price'] = new_original_price if not new_min_price and not new_max_price else None
            if new_sale_price is not None:
                item['sale_price'] = new_sale_price if not new_min_sale_price and not new_max_sale_price else None
            if new_min_price is not None:
                item['min_price'] = new_min_price  # Update min price if provided
            if new_max_price is not None:
                item['max_price'] = new_max_price  # Update max price if provided
            if new_min_sale_price is not None:
                item['min_sale_price'] = new_min_sale_price  # Update min sale price if provided
            if new_max_sale_price is not None:
                item['max_sale_price'] = new_max_sale_price  # Update max sale price if provided
            if new_room is not None:
                item['room'] = new_room
            if new_url is not None:
                item['url'] = new_url
            if new_image_url is not None:
                item['image_url'] = new_image_url  # Update image URL if provided
            updated = True
            break
    if updated:
        save_furniture_list(furniture_list)
        return True  # Indicates the item was updated
    return False  # No item with that ID was found

