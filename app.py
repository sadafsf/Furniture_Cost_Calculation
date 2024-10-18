from flask import Flask, render_template, request, redirect, url_for, flash
import furniture
from scraper import fetch_furniture_data

from collections import defaultdict

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

@app.route('/')
def index():
    furniture_list = furniture.load_furniture_list()

    # Group furniture by rooms and calculate total price for each room
    room_furniture = defaultdict(list)
    overall_total_price = 0

    for item in furniture_list:
        room = item['room']

        # Calculate the price: display min and max price if available, otherwise use sale price or original price
        if item.get('sale_price'):
            price = item['sale_price']
        elif item.get('min_price') and item.get('max_price'):
            price = float(item['min_price'])  # Use the min_price for total price calculation, but display both
        else:
            price = item.get('original_price', 0)

        room_furniture[room].append(item)
        overall_total_price += price

    # Calculate total price per room
    room_totals = {room: sum(
        float(item.get('sale_price') or item.get('min_price') or item.get('original_price', 0))
        for item in items)
        for room, items in room_furniture.items()}

    return render_template('index.html', room_furniture=room_furniture, room_totals=room_totals, overall_total_price=overall_total_price)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        furniture_list = furniture.load_furniture_list()

        # Check if URL was provided
        url = request.form['url']
        if url:
            # Fetch furniture data including name, sale price, original price, min/max prices, and image URL
            name, sale_price, original_price, min_price, max_price, image_url, fetched_url = fetch_furniture_data(url)

            # Debug print the values to ensure correct fetching
            print(f"Fetched Data - Name: {name}, Sale Price: {sale_price}, Original Price: {original_price}, Min Price: {min_price}, Max Price: {max_price}")

            if not name:
                flash('Failed to fetch furniture data from the provided URL.')
                return redirect(url_for('add_item'))
        else:
            # Manual entry of the data
            name = request.form['name']
            original_price = float(request.form['price']) if request.form['price'] else None
            sale_price = None
            image_url = request.form['image_url']

        room = request.form['room']
        furniture.add_furniture_with_details(furniture_list, name, original_price, sale_price, room, url, image_url)
        flash(f'{name} added successfully.')
        return redirect(url_for('index'))

    return render_template('add_item.html')



@app.route('/update_item/<furniture_id>', methods=['GET', 'POST'])
def update_item(furniture_id):
    furniture_list = furniture.load_furniture_list()
    if request.method == 'POST':
        original_price = float(request.form['original_price'])
        sale_price = float(request.form['sale_price']) if request.form['sale_price'] else None
        room = request.form['room']
        url = request.form['url']
        image_url = request.form['image_url']
        success = furniture.update_furniture(furniture_list, furniture_id, new_original_price=original_price, 
                                             new_sale_price=sale_price, new_room=room, new_url=url,
                                             new_image_url=image_url)
        if success:
            flash(f'Item updated successfully.')
        else:
            flash(f'Failed to update item.')
        return redirect(url_for('index'))
    return render_template('update_item.html', name=furniture_id)

@app.route('/remove_item/<furniture_id>', methods=['GET'])
def remove_item(furniture_id):
    furniture_list = furniture.load_furniture_list()
    success = furniture.remove_furniture(furniture_list, furniture_id)
    if success:
        flash(f'Item removed successfully.')
    else:
        flash(f'Failed to remove item.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
