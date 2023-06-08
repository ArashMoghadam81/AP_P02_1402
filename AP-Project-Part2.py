#importing required modules and libraris
from flask import Flask, render_template, request, redirect, session, flash,url_for
import os
from werkzeug.utils import secure_filename
import requests

# using api to exchange USD to IRR
api_key = "freeLLAbxptI2n0R0VwHjK7fc4laNBpT"
url = f"http://api.navasan.tech/latest/?api_key={api_key}"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()

else:
    print("API request failed:", response.status_code)

for d in data:
    if d == "usd_sell":
        curruncy_index=int(data[d]['value']+'0')

# print(curruncy_index)

app = Flask(__name__)
app.secret_key = "your_secret_key"
upload_folder = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = upload_folder
products = []
users = {}
cart = []


@app.route('/')
def home():
    return render_template('Base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract login credentials
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username exists in the users dictionary
        if username in users:
            # Check if the password matches the stored password
            if users[username]['password'] == password:
                # Store user data in session
                session['username'] = username
                session['role'] = users[username]['role']
                return redirect('/Dashboard')
        
        # If login failed, show an error message
        else:
            error_message = "Invalid username or password"
            return render_template('login.html', error_message=error_message)
    # Render the login form for GET requests
    return render_template('login.html')


@app.route('/Dashboard')
def dashboard():
    if 'username' in session:
        role = session['role']
        if role == 'seller':
            # Fetch seller-specific data, such as their listed products
            # Display the seller dashboard
            return render_template('Seller_dashboard.html', username=session['username'])
        elif role == 'buyer':
            all_products = products
            # Fetch buyer-specific data, such as recently added products
            # Display the buyer dashboard
            return render_template('Buyer_dashboard.html', username=session['username'], products=all_products)

    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract registration data
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Either 'buyer' or 'seller'

        # Create a new user dictionary
        user = {
            'username': username,
            'password': password,
            'role': role
        }

        # Store the user data in the users dictionary with the username as the key
        users[username] = user

        return redirect('/login')

    # Render the registration form for GET requests
    return render_template('register.html')


@app.route('/seller_dashboard')
def seller_dashboard():
    if 'username' in session and session['role'] == 'seller':
        seller_products = []  # List to store products specific to the seller

        # Fetch products specific to the seller from the global products list
        for product in products:
            if product['seller'] == session['username']:
                seller_products.append(product)

        return render_template('seller_dashboard.html', products=seller_products)

    return redirect('/login')


@app.route('/seller_dashboard_add')
def seller_dashboard_add():
    if 'username' in session and session['role'] == 'seller':
        seller_products = []  # List to store products specific to the seller

        # Fetch products specific to the seller from the global products list
        for product in products:
            if product['seller'] == session['username']:
                seller_products.append(product)

        return render_template('seller_dashboard_add.html', products=seller_products)

    return redirect('/login')


@app.route('/Add_product_seller', methods=['GET', 'POST'])
def add_product_seller():
    if 'username' in session and session['role'] == 'seller':
        if request.method == 'POST':
            # Extract product data from the form
            name = request.form['name']
            price = float(request.form['price'])
            image = request.files['image']

            # Save the uploaded image and retrieve the filename
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Create a new product dictionary
            product = {
                'name': name,
                'price': price,
                'image': filename,
                'seller': session['username'],  # Store the seller's username
                'gheymat': (price*curruncy_index)

            }

            if any(p['name'] == product['name'] for p in products):
                flash('Product already exists')
            else:
                # Append the new product to the global products list
                products.append(product)

            img = url_for('static', filename='uploads/' + filename)
            return redirect('/seller_dashboard_add')

        return render_template('add_product.html')

    return redirect('/login')


@app.route('/remove_product_seller/<product_name>', methods=['POST'])
def remove_product_seller(product_name):
    if 'username' in session and session['role'] == 'seller':
        # Find the product in the products list by name
        for product in products:
            if product['name'] == product_name and product['seller'] == session['username']:
                products.remove(product)
                break

        if products==[]:
            return redirect('/seller_dashboard')
        
        else:
            return redirect('/seller_dashboard_add')

    return redirect('/login')


@app.route('/buyer_dashboard')
def buyer_dashboard():
    if 'username' in session and session['role'] == 'buyer':
        all_products = products
        return render_template('buyer_dashboard.html', cart=cart, products=all_products)
    return redirect('/login')


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'username' in session and session['role'] == 'buyer':
        if request.method == 'POST':
            product_name = request.form['product_name']
            quantity = request.form['quantity']
            
            # Find the product in the products list using the product_name
            product = next((p for p in products if p['name'] == product_name), None)
            
            if product:
                # Create a cart_item dictionary with the product details and quantity
                cart_item = {
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity,
                    'image': product['image'], # Add the image information
                    'buyer': session['username'],
                    'gheymat': product['gheymat']
                }
                
                # Add the cart_item to the buyer's cart
                cart.append(cart_item)
                
                flash('Product added to your cart', 'buyer_dashboard')
                return redirect('/buyer_dashboard')
            
            else:
                flash('Invalid product')
        
        return redirect('/buyer_dashboard')
    return redirect('/login')


@app.route('/cart')
def buyer_cart():
    if 'username' in session and session['role'] == 'buyer':
        buyer_products = []
        total_cost = 0
        for product in cart:
            if product['buyer'] == session['username']:
                buyer_products.append(product)
                total_cost += int(product['quantity'])*float(product['price'])

        total_gheymat = (float(total_cost)*curruncy_index)
        session['buyer_products'] = buyer_products  # Store buyer_products in session
        session['total_cost'] = total_cost

        return render_template('Cart.html',total_cost=total_cost , total_gheymat=total_gheymat,cart=buyer_products, curruncy_index=curruncy_index)
    return redirect('/login')


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'username' in session and session['role'] == 'buyer':
        if request.method == 'POST':
            product_name = request.form['product_name']
            cart[:] = [item for item in cart if item['name'] != product_name]

        flash('Product removed', 'remove')
        return redirect('/cart')
    return redirect('/login')


@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    if 'username' in session and session['role'] == 'buyer':
        if request.method == 'POST':
            product_name = request.form['product_name']
            quantity = int(request.form['quantity'])
            
            # Find the product in the buyer's cart
            for item in cart:
                if item['name'] == product_name:
                    item['quantity'] = quantity
                    break            
            flash('Quantity updated', 'update')
        
        return redirect('/cart')
    return redirect('/login')


@app.route('/purchased')
def purchase():
    if cart==[]:
            flash('Please add product to your cart!', 'empty')
            return redirect('/cart')
    
    else:       
        if 'username' in session and session['role'] == 'buyer':
            buyer_products = session.pop('buyer_products', [])  # Retrieve and clear buyer_products from session

            # Remove purchased products from the cart
            cart[:] = [item for item in cart if item not in buyer_products]
            flash('Thank you! Purchase was Successful.', 'purchase')
            return redirect('/cart')

    return redirect('/login')


@app.route("/logout")
def logout():

    flash("You have been logged out!")
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)

