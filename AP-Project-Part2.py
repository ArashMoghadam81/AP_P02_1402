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

@app.route("/logout")
def logout():

    flash("You have been logged out!")
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
