from flask import Flask, render_template, request, redirect, url_for, flash
import furniture
from scraper import fetch_furniture_data


app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

@app.route('/')
def index():
    furniture_list = furniture.load_furniture_list()
    total_price = sum(item['sale_price'] or item['original_price'] for item in furniture_list)
    return render_template('index.html', furniture_list=furniture_list, total_price=total_price)


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
        furniture.add_furniture_with_sale(furniture_list, name, original_price, sale_price, room, url)
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