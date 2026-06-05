from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename
import pickle
import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ---------------- UPLOAD FOLDER ----------------
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- DATABASE ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dipak@123",
    database="farmer_table"
)

cursor = db.cursor()

# ---------------- LOAD AI MODEL ----------------
model = pickle.load(open("model/model.pkl","rb"))

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template("login.html")

# ---------------- SIGNUP PAGE ----------------
@app.route('/signup')
def signup_page():
    return render_template("signup.html")

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    address = request.form['address']   # ✅ IMPORTANT
    role = request.form['role']

    query = "INSERT INTO users (name,email,password,address,role) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(query,(name,email,password,address,role))
    db.commit()

    return redirect('/')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query,(email,password))
    user = cursor.fetchone()

    if user:
        session['user_id'] = user[0]
        session['name'] = user[1]
        session['role'] = user[4]
        session['address'] = user[5]   # ✅ correct index

        if user[4] == "farmer":
            return redirect('/farmer')
        else:
            return redirect('/buyer')
    else:
        return "Login Failed"

# ---------------- FARMER DASHBOARD ----------------
@app.route('/farmer')
def farmer():
    if 'user_id' not in session:
        return redirect('/')
    return render_template("farmer_dashboard.html")

# ---------------- BUYER DASHBOARD ----------------
@app.route('/buyer')
def buyer():
    if 'user_id' not in session:
        return redirect('/')
    return render_template("buyer_dashboard.html")


# ---------------- CHAT PAGE ----------------
@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('chat.html')

# ---------------- ADD PRODUCT ----------------
@app.route('/add', methods=['POST'])
def add_product():

    if 'user_id' not in session:
        return redirect('/')

    name = request.form['name']
    price = int(request.form['price'])
    description = request.form['description']
    image = request.files['image']
    lat = request.form.get('lat')
    lng = request.form.get('lng')

    print("LOCATION:", lat, lng)

    # ✅ farmer info from session
    farmer_name = session.get('name')
    farmer_address = session.get('address')

    # save image
    filename = secure_filename(image.filename)
    new_name = str(len(os.listdir(UPLOAD_FOLDER))) + "_" + filename

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
    image.save(image_path)

    # ---------------- AI PRICE ----------------
    crop_map = {
        "tomato":0,
        "onion":1,
        "potato":2,
        "wheat":3,
        "rice":4
    }

    crop_val = crop_map.get(name.lower(),0)
    district_val = 0
    month = datetime.datetime.now().month

    ai_price = int(model.predict([[crop_val, district_val, month]])[0])

    # ---------------- SAVE PRODUCT ----------------
    query = """
    INSERT INTO products 
    (name, price, ai_price, image, description, farmer_name, farmer_address, lat, lng) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

    cursor.execute(query,(name, price, ai_price, new_name, description, farmer_name, farmer_address, lat, lng))
    db.commit()

    return redirect('/farmer')

# ---------------- GET PRODUCTS ----------------
@app.route('/products')
def products():

    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    data = cursor.fetchall()

    result = []

    for row in data:
        result.append({
            "id":row[0],
            "name":row[1],
            "price":row[2],
            "ai_price":row[3],
            "image":row[4],
            "description":row[5],
            "farmer_name":row[6],
            "farmer_address":row[7],
            "lat": row[8],#added lat and lng to products table and fetching here
            "lng": row[9]
        })

    return jsonify(result)

# ---------------- BUY PRODUCT ----------------
@app.route('/buy', methods=['POST'])
def buy():

    if 'user_id' not in session:
        return jsonify({"msg":"login first"})

    data = request.get_json()

    return jsonify({
        "user": session['name'],
        "product": data['product'],
        "price": data['price']
    })

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)