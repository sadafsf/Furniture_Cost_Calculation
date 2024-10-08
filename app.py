from flask import Flask, render_template, request, redirect, url_for, flash
from furniture import load_furniture_list, add_furniture_with_sale, remove_furniture, update_furniture
from scraper import fetch_furniture_data

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

@app.route('/')
def index():
    furniture_list = load_furniture_list()

    # Handle items that may have sale and original price or just a single price
    total_price = sum(
        (
            (item.get('sale_price') or 0) + (item.get('original_price') or 0)
        ) / 2
        for item in furniture_list
    )

    return render_template('index.html', furniture_list=furniture_list, total_price=total_price)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        url = request.form['url'].strip()

        if url:
            # Fetch furniture name, sale price, original price, and URL from the provided URL
            name, sale_price, original_price, url = fetch_furniture_data(url)

            if name and (sale_price or original_price):
                room = request.form['room']
                add_furniture_with_sale(load_furniture_list(), name, original_price, sale_price, room, url)
                flash(f'{name} added successfully with sale price ${sale_price} and original price ${original_price}!')
            else:
                flash("Could not extract furniture data from the provided URL. Please try manually.")
                return redirect(url_for('add_item'))
        else:
            # Handle manual entry (single price)
            name = request.form['name'].strip()
            price = float(request.form['price'].strip())
            room = request.form['room'].strip()
            add_furniture_with_sale(load_furniture_list(), name, price, None, room, None)
            flash(f'{name} added successfully!')

        return redirect(url_for('index'))

    return render_template('add_item.html')

@app.route('/update/<string:name>', methods=['GET', 'POST'])
def update_item(name):
    if request.method == 'POST':
        new_original_price = float(request.form['original_price']) if request.form['original_price'] else None
        new_sale_price = float(request.form['sale_price']) if request.form['sale_price'] else None
        new_room = request.form['room']
        new_url = request.form['url']

        if update_furniture(load_furniture_list(), name, new_original_price, new_sale_price, new_room, new_url):
            flash(f'{name} has been updated successfully!')
        else:
            flash(f'{name} not found.')

        return redirect(url_for('index'))

    return render_template('update_item.html', name=name)

@app.route('/remove/<string:name>')
def remove_item(name):
    furniture_list = load_furniture_list()
    if remove_furniture(furniture_list, name):
        flash(f'{name} has been removed.')
    else:
        flash(f'{name} not found.')
    return redirect(url_for('index'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
