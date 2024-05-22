from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, db

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize Firebase Admin SDK
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://alzheimerdetectionsystem-default-rtdb.firebaseio.com/'
})

# Admin credentials
admin_username = "admin"
admin_password = "admin"

# Function to generate user id and add user details to the database
def generate_user_id(name, age, location):
    # Get the current count of users
    user_count = db.reference('admin').get()
    if user_count:
        user_count = len(user_count) + 1  # Increment by 1 for next user
    else:
        user_count = 1  # First user
    # Generate user id with format "P000"
    user_id = "P{:03d}".format(user_count)
    # Add user details to the database
    db.reference('users').child(user_id).set({
        'name': name,
        'age': age,
        'location': location
    })
    return user_id

# Route for landing page
@app.route('/')
def landing():
    return render_template('landing.html')

# Route for admin login
@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == admin_username and password == admin_password:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

# Route for admin dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    action = request.args.get('action')
    
    if request.method == 'POST':
        if action == 'create':
            # Create new user data
            name = request.form['name']
            age = request.form['age']
            location = request.form['location']
            user_id = generate_user_id(name, age, location)
            return redirect(url_for('admin_dashboard', action='existing'))  # Redirect to existing users
    
    users = None
    if action == 'existing':
        # Retrieve all user data
        users = db.reference('users').get()
    return render_template('dashboard.html', action=action, users=users)


if __name__ == '__main__':
    app.run(debug=True)
