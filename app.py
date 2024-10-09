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
        # Use sale price if it exists, otherwise use the original price
        price = item['sale_price'] if item['sale_price'] else item['original_price']
        room_furniture[room].append(item)
        overall_total_price += price

    # Calculate total price per room
    room_totals = {room: sum(item['sale_price'] if item['sale_price'] else item['original_price'] for item in items)
                   for room, items in room_furniture.items()}

    return render_template('index.html', room_furniture=room_furniture, room_totals=room_totals, overall_total_price=overall_total_price)


@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        furniture_list = furniture.load_furniture_list()

        # Check if URL was provided
        url = request.form['url']
        if url:
            # Fetch furniture data
            name, sale_price, original_price, fetched_url = fetch_furniture_data(url)
            if not name:
                flash('Failed to fetch furniture data from the provided URL.')
                return redirect(url_for('add_item'))
        else:
            # Manual entry of the data
            name = request.form['name']
            original_price = float(request.form['price']) if request.form['price'] else None
            sale_price = None

        room = request.form['room']
        furniture.add_furniture_with_sale(furniture_list, name, original_price, room, url, sale_price)
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
        success = furniture.update_furniture(furniture_list, furniture_id, new_original_price=original_price, new_sale_price=sale_price, new_room=room, new_url=url)
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