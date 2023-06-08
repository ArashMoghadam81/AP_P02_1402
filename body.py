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




