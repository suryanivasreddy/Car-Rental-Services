from flask import Flask, render_template, request, redirect, url_for, flash ,session, jsonify
from pymongo import MongoClient
import datetime
from werkzeug.utils import secure_filename
import os
from bson import ObjectId
"""
CAR RENTAL SERVICE - MINI PROJECT KITS's (CSE)

Developed by:
Batch 12, Section A
- T. Jayasree (21281A0511)
- R. Rakshitha (21281A0520)
- S. Surya Nivas Reddy (21281A0553)
- B. Krishnaveni (21281A0559)

For any queries, please contact: 7093220647
"""
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/ad2')
db = client['car_rentaldb']  # Database name
cars_collection = db['cars']
users_collection = db['users']  # Collection name
selfbook_collection = db['selfbook']
driverbook_collection = db['driverbook']  # Collection name for driver bookings
contacts_collection = db.contacts


# Routes
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pwd']
        
        # Check if user exists in the database
        user = users_collection.find_one({'email': email, 'password': password})
        
        if user:
            session['user'] = user['email']
            flash('You have been logged in successfully.', 'success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard if login is successful
        else:
            error_message = "Invalid credentials. Please try again."  # Set error message
    
    return render_template('login.html', error_message=error_message)  # Pass error message to template


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        # User is not logged in, show the dashboard but with a login button
        return render_template('dashboard.html', logged_in=False)
    else:
        # User is logged in, show the dashboard with a logout button
        return render_template('dashboard.html', logged_in=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collect form data
        name = request.form['user']
        email = request.form['email']
        password = request.form['pwd']
        repassword = request.form['rpwd']
        gender = request.form['r']
        phone = request.form['phn']
        address = request.form.get('address', '')

        # Check if email already exists
        existing_user = users_collection.find_one({'email': email})
        
        if existing_user:
            # *** Highlighted Change *** - Email already exists
            flash("Email already used, please use another email.", "error")
            return redirect(url_for('register'))

        if password != repassword:
            # *** Highlighted Change *** - Password mismatch
            flash("Password and Re-entered password do not match.", "error")
            return redirect(url_for('register'))

        # Insert user data into MongoDB
        user_data = {
            'name': name,
            'email': email,
            'password': password,
            'gender': gender,
            'phone': phone,
            'address': address
        }
        users_collection.insert_one(user_data)

        # *** Highlighted Change *** - Registration successful
        flash("Registration successful.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

      
@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.pop('user', None)
    # You can also flash a message if you want
    flash('You have been logged out successfully.', 'success')
    # Redirect to the login page or any other page like the homepage
    return redirect(url_for('login'))

@app.route('/about_us')
def about_us():
      if 'user' not in session:
        # User is not logged in, show the dashboard but with a login button
         return render_template('about_us.html', logged_in=False)
      else:
        # User is logged in, show the dashboard with a logout button
       return render_template('about_us.html', logged_in=True)

@app.route('/carlists')
def carlists():
    if 'user' not in session:
        return redirect(url_for('login'))
    client = MongoClient('mongodb://localhost:27017/')
    cars = cars_collection.find()
    return render_template('carlists.html', cars=cars)


@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    logged_in = 'user' in session
    if request.method == 'POST':
        # Collect form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Insert the form data into MongoDB
        contact_data = {
            'name': name,
            'email': email,
            'message': message
        }
        contacts_collection.insert_one(contact_data)

        # Flash success message and redirect
        flash('Thank you for reaching out! We will get back to you soon.', 'success')
        return redirect(url_for('contact_us'))

    return render_template('contact_us.html', logged_in=logged_in)

# Route to display feedback (retrieving the data)
@app.route('/feed_back')
def feed_back():
    # Fetch all contact form submissions from MongoDB
    feedback_data = contacts_collection.find()
    return render_template('feed_back.html', feedbacks=feedback_data)


@app.route('/selection')
def selection():
    return render_template('selection.html')

@app.route('/selfbook', methods=['GET', 'POST'])
def selfbook():
    if request.method == 'POST':
        book ={
             'name': request.form['name'],
             'email': request.form['email'],
             'phone': request.form['phone'],
             'license': request.form['license'],
             'pickup_date': request.form['pickup_date'],
             'dropoff_date': request.form['dropoff_date'],
             'car_model' : request.form['car_model'],
             'payment_UTR' : request.form['payment_UTR'],
             'notes' : request.form.get('notes', '')
        }
    

        # Insert the booking data into the 'selfbook' collection
        selfbook_collection.insert_one(book)
        flash('Booking is confirmed if payment is successful.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('selfbook.html')

@app.route('/driverbook', methods=['GET', 'POST'])
def driverbook():
    if request.method == 'POST':
        book ={
             'name': request.form['name'],
             'email': request.form['email'],
             'phone': request.form['phone'],
             'driver_name': request.form['driver_name'],
             'pickup_date': request.form['pickup_date'],
             'dropoff_date': request.form['dropoff_date'],
             'car_model' : request.form['car_model'],
             'payment_UTR' : request.form['payment_UTR'],
             'notes' : request.form.get('notes', '')
        }
    

        # Insert the booking data into the 'selfbook' collection
        driverbook_collection.insert_one(book)
        flash('Booking is confirmed if payment is successful.', 'success')
        # Process the booking details and save to the database if neededA
        return redirect(url_for('dashboard'))

    return render_template('driverbook.html')



@app.route('/drivers')
def drivers():
    client = MongoClient('mongodb://localhost:27017/')
    cars = cars_collection.find()
    return render_template('drivers.html', cars=cars)

"""
CAR RENTAL SERVICE - MINI PROJECT KITS's (CSE)

Developed by:
Batch 12, Section A
- T. Jayasree (21281A0511)
- R. Rakshitha (21281A0520)
- S. Surya Nivas Reddy (21281A0553)
- B. Krishnaveni (21281A0559)

For any queries, please contact: 7093220647
"""

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error_message = None
    if request.method == 'POST':
        adminname = request.form['adminname']
        password = request.form['pwd']
        
        # Check if user exists in the database

        if adminname == 'carowner' and password == 'Car@500':  # Replace with actual authentication logic
            return redirect('admin_dashboard')
        else:
            error_message = "Invalid credentials. Please try again."  # Set error message
    
    return render_template('admin_login.html', error_message=error_message)  # Pass error message to template

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to display the add car page and process form data
@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        car_name = request.form['name']
        price = request.form['price']
        mileage = request.form['mileage']
        driver_name = request.form['driver_name']
        driver_price = request.form['driver_price']
        driver_experience = request.form['driver experience']
        notes = request.form.get('notes', '')

        # Handling image upload
        if 'image' not in request.files:
            flash('No image file part')
            return redirect(request.url)
        
        image_file = request.files['image']

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            # Create car data object to store in MongoDB
            car_data = {
                'name': car_name,
                'image': image_path,
                'price': price,
                'mileage': mileage,
                'driver_name': driver_name,
                'driver_price': driver_price,
                'driver_experience': driver_experience,
                'notes': notes
            }

            # Insert car data into MongoDB
            cars_collection.insert_one(car_data)

            flash('Car added successfully!')
            return redirect(url_for('admin_dashboard'))

        else:
            flash('Invalid file type. Only images are allowed.')
            return redirect(request.url)

    return render_template('add_car.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    # Retrieve all cars
    cars = cars_collection.find()
    return render_template('admin_dashboard.html', cars=cars)

@app.route('/delete_car/<car_id>')
def delete_car(car_id):
    try:
        # Delete the car from the collection
        cars_collection.delete_one({'_id': ObjectId(car_id)})
        flash('Car deleted successfully!')
    except Exception as e:
        flash('Error while deleting the car.')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/orders', methods=['GET'])
def admin_orders():
    # Retrieve all bookings from the 'selfbook' collection
    bookings = list(selfbook_collection.find())

    # Send the bookings data to the 'admin_orders.html' template
    return render_template('admin_orders.html', orders=bookings)

@app.route('/withdriver', methods=['GET'])
def withdriver():
    # Retrieve all bookings from the 'selfbook' collection
    bookings = list(driverbook_collection.find())

    # Send the bookings data to the 'admin_orders.html' template
    return render_template('withdriver.html', orders=bookings)



# Edit Car Route
@app.route('/edit/<car_id>', methods=['GET'])
def edit_car(car_id):
    car = cars_collection.find_one({'_id': ObjectId(car_id)})
    return render_template('edit.html', car=car)


@app.route('/update/<car_id>', methods=['POST'])
def update_car(car_id):
    name = request.form.get('name')
    price = request.form.get('price')
    mileage = request.form.get('mileage')
    driver_name = request.form.get('driver_name')
    driver_experience = request.form.get('driver_experience')
    driver_price = request.form.get('driver_price')
    notes = request.form.get('notes')
    
    # Handle optional image upload
    image = request.files.get('image')
    if image and image.filename != '':
        # Define the upload folder path
        upload_folder = os.path.join(app.root_path, 'static/uploads')
        
        # Ensure the directory exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Generate the absolute path for the image
        image_path = os.path.join(upload_folder, image.filename)
        
        # Save the image to the file path
        image.save(image_path)
        
        # Store the relative path to the image in the database
        relative_image_path = '/static/uploads/' + image.filename
        cars_collection.update_one({'_id': ObjectId(car_id)}, {'$set': {'image': relative_image_path}})

    # Update other car details
    cars_collection.update_one({'_id': ObjectId(car_id)}, {
        '$set': {
            'name': name,
            'price': price,
            'mileage': mileage,
            'driver_name': driver_name,
            'driver_experience': driver_experience,
            'driver_price': driver_price,
            'notes': notes
        }
    })

    flash('Car details updated successfully!')
    return redirect(url_for('admin_dashboard'))




if __name__ == '__main__':
    app.run(debug=True)
"""
CAR RENTAL SERVICE - MINI PROJECT KITS's (CSE)

Developed by:
Batch 12, Section A
- T. Jayasree (21281A0511)
- R. Rakshitha (21281A0520)
- S. Surya Nivas Reddy (21281A0553)
- B. Krishnaveni (21281A0559)

For any queries, please contact: 7093220647
"""