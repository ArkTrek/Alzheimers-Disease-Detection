from flask import Flask, render_template, request, redirect, url_for, session, flash
import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import tensorflow as tf
from tensorflow_addons.metrics import F1Score
import matplotlib.pyplot as plt
from io import BytesIO
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import cv2
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://classify.roboflow.com",
    api_key="wcDKxxCya6kJIpda6sK2"
)



app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Initialize Firebase Admin SDK
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://alzheimerdetectionsystem-default-rtdb.firebaseio.com/'})

users = {
    'Ashwin': {'username': 'Ashwin', 'password': 'Abc123'},
    'Shonin': {'username': 'Shonin', 'password': 'abc'},
    'Admin': {'username': 'admin', 'password': 'admin'},
    'Gokul': {'username': 'gokul', 'password': 'gokul'}
}

admin_username = "admin"
admin_password = "admin"

@app.route('/')
def index():
    return render_template('loginn.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user is in the users dictionary
        if username in users:
            user_data = users[username]
            if password == user_data['password']:
                session['logged_in'] = True
                return redirect(url_for('success'))

        # Check if the user is the admin
        if username == admin_username and password == admin_password:
             session['logged_in'] = True
             return redirect(url_for('admin_dashboard'))

        # If username or password is incorrect, show error message
        return render_template('login.html', error="Invalid username or password")

    return render_template('index.html')

@app.route('/success')
def success():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # username = session.get('name')
    # user_data = fetch_user_data(username)
    
    # Process user_data or render template accordingly
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # get the answers submitted by the user
    q1 = request.form['q1']
    q2 = request.form['q2']
    q3 = request.form['q3']
    q4 = request.form['q4']
    q5 = request.form['q5']
    q6 = request.form['q6']

    # calculate the score
    score = 0
    if q1 == 'a':
        score += 5
    elif q1 == 'b':
        score += 3
    elif q1 == 'c':
        score += 0

    if q2 == 'a':
        score += 5
    elif q2 == 'b':
        score += 3
    elif q2 == 'c':
        score += 0

    if q3 == 'a':
        score += 8
    elif q3 == 'b':
        score += 5
    elif q3 == 'c':
        score += 3
    elif q3 == 'd':
        score += 0

    if q4 == 'a':
        score += 3
    elif q4 == 'b':
        score += 1
    elif q4 == 'c':
        score += 0

    if q5 == 'a':
        score += 8
    elif q5 == 'b':
        score += 5
    elif q5 == 'c':
        score += 3
    elif q5 == 'd':
        score += 0

    if q6 == 'a':
        score += 8
    elif q6 == 'b':
        score += 5
    elif q6 == 'c':
        score += 3
    elif q6 == 'd':
        score += 0

    if score > 24:
        return render_template('resultPage.html', score=score, total=37)
    else:
        return render_template('detectionPage.html')

# Route for rendering the detection.html template
@app.route('/detectionPage')
def detection_page():
    return render_template('detectionPage.html')

# Route for MSMETest page
@app.route('/MSMETest')
def msmetest():
    return render_template('MSMETest.html')

from flask import render_template

@app.route('/tips')
def tips():
    return render_template('tips.html')

from flask import render_template

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/DD1')
def DD1():
    return render_template('DD1.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/create_user')
def create_user():
    return render_template('create_user.html')

@app.route('/existing')
def existing_patients():
    return render_template('existing_patients.html', users=users)

@app.route('/DD1.html')
def dd1():
    return render_template('DD1.html')

@app.route('/loginn')
def loginn():
    return render_template('loginn.html')



def add_new_doctor(name, address, phone, email):
    try:
        ref = db.reference('doctors')
        new_doctor_ref = ref.push({
            'name': name,
            'address': address,
            'phone': phone,
            'email': email
        })
        return True
    except Exception as e:
        print("Error adding new doctor:", e)
        return False

# Function to delete doctor data from Firebase RTDB
def delete_doctor(doctor_id):
    try:
        ref = db.reference('doctors')
        ref.child(doctor_id).delete()
        return True
    except Exception as e:
        print("Error deleting doctor:", e)
        return False

@app.route('/doctors')
def doctors():
    doctors_list = get_doctors_from_rtdb()
    return render_template('doctors.html', doctors=doctors_list)


def get_doctors_from_rtdb():
    try:
        ref = db.reference('doctors')
        doctors_data = ref.get()
        doctors_list = []  # List to store doctor data
        if doctors_data:
            for doctor_id, doctor_info in doctors_data.items():
                doctor_info['id'] = doctor_id  # Add doctor ID to the info
                doctors_list.append(doctor_info)
        return doctors_list
    except Exception as e:
        print("Error retrieving doctors data:", e)
        return []
    
@app.route('/delete-doctor/<doctor_id>', methods=['POST'])
def delete_doctor_route(doctor_id):
    if delete_doctor(doctor_id):
        return redirect(url_for('doctors'))
    else:
        return render_template('error.html', error="Failed to delete doctor")

# @app.route('/doctors')
# def doctors():
#     # Dummy data for demonstration
#     doctors_list = [
#         {'name': 'DR RAMESH CV ', 'address': 'Thalassery,Kannur', 'phone': '08792485418', 'email': 'Ramesh.doe@example.com'},
#         {'name': 'DR KK NIRMAL RAJ', 'address': '456 Elm St, City, Country', 'phone': '07925897713', 'email': 'nirmal.smith@example.com'},
#         {'name': 'DR SUJITH OVALLATH', 'address': 'Kannur,kerala', 'phone': '07942655943 ','email': 'sujith.oval@example.com'},
#         {'name': 'DR GOKUL PREM', 'address': 'Kannur,kerala', 'phone': '07942784243 ','email': 'gokul@example.com'},
#         {'name': 'DR UNNIKRISHAN P', 'address': 'Thalassery,kerala', 'phone': '0984789243 ','email': 'UNNI@example.com'},
#         {'name': 'DR RAMESH BASH', 'address': 'Thalassery,kerala', 'phone': '0984789243 ', 'email': 'bashi@example.com'},
#         # Add more doctor entries as needed
#     ]
#     # if request.method == 'POST':
#     #     name = request.form['name']
#     #     address = request.form['address']
#     #     phone = request.form['phone']
#     #     mail = request.form['mail']
#     #     doctors_list = [{'name': name, 'address': address, 'phone': phone, 'mail': mail}]
#     #     return render_template('doctors.html', doctors=doctors_list)
#     # name = request.form['name']
#     # address = request.form['address']
#     # phone = request.form['phone']
#     # email = request.form['email']
#     # ref = db.reference('dr').child('dr1')
#     # ref.update({'name': name})
#     # ref.update({'address': address})
#     # ref.update({'phone': phone})
#     # ref.update({'email': email})
#     # listt = [{'name': name, 'address': address, 'phone': phone, 'email': email}]

#     return render_template('doctors.html', doctors=doctors_list)

@app.route('/add-doctor', methods=['POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        if add_new_doctor(name, address, phone, email):
            return redirect(url_for('doctors'))
        else:
            return render_template('error.html', error="Failed to add doctor")

def adddr():
    name = request.form['name']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    ref = db.reference('dr').child('dr1')
    ref.update({'name': name})
    ref.update({'address': address})
    ref.update({'phone': phone})
    ref.update({'email': email})
    print("Dr. Added Succefully!")

@app.route('/result', methods=["POST"])
def result():
    model = tf.keras.models.load_model("./modelFile/alzhemers.h5")
    CLASSES = ['mildDemented', 'ModerateDemented', 'NonDemented', 'VeryMildDemented']
    
    file = request.files['image']
    # file_contents = file.read()
    file_path = "static\\css\\img\\result.jpg"
    file.save(file_path)

    # image = cv2.imread(file_path)

    # Check if the image is loaded successfully
    if file_path is None:
        print("Error: Unable to load the image.")
        result = "Error: No image passed."

    # Check if the image has gray values
    val = has_grey_values(file_path)
    if val == True:
        # img = tf.keras.preprocessing.image.load_img(file_path, target_size=(176, 176))
        # x = tf.keras.preprocessing.image.img_to_array(img)
        # x = np.expand_dims(x, axis=0)

        # Perform inference using the model
        result = CLIENT.infer(file_path, model_id="mode5/1")
        result = result['predicted_classes']
    else:
        result = "Not an MRI Scan!"
        flash("Error: Not an MRI Scan!")
        # return redirect(request.url)

    generate_pdf(request.form['patient_name'], request.form['patient_age'], result)
    return render_template('res.html', result=result, val=val)

import cv2

def has_grey_values(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    # Check if the image is loaded successfully
    if image is None:
        print("Error: Unable to load the image at", image_path)
        return False

    # Convert the image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    lower_gray = np.array([0, 0, 50])
    upper_gray = np.array([180, 30, 220])
    
    mask = cv2.inRange(hsv_image, lower_gray, upper_gray)
    
    num_grey_pixels = np.count_nonzero(mask)
    
    threshold = 0.01 * hsv_image.size 
    val = num_grey_pixels > threshold
    print("Value: ", val)
    return val

    

def generate_pdf(patient_name, patient_age, result):
    global pdf_counter
    pdf_counter = 0
    pdf_filename = f"report_{pdf_counter}.pdf"
    pdf_counter += 1
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading1']

    title = Paragraph("<b>Medical Report</b>", bold_style)
    elements.append(title)
    elements.append(Paragraph("<br/><br/>", normal_style))

    extra_details = ""
    if result == "mildDemented":
        extra_details = "In the early stages of Alzheimer's disease, individuals typically experience mild cognitive impairment characterized by subtle but noticeable changes in memory, cognition, and behavior. Memory loss, especially in recent events, is a prominent feature, along with difficulties in problem-solving and decision-making. Language and communication skills may also decline, leading to challenges in verbal expression and comprehension. Mood swings, personality changes, and occasional lapses in judgment may become apparent, although individuals can often still manage daily activities independently. Recognizing these symptoms early allows for timely intervention and support to help individuals and their families navigate the progression of the disease with greater understanding and preparedness."
        result = "Mild Demented"
    elif result == "ModerateDemented":
        extra_details = "In the moderately demented state of Alzheimer's disease, individuals experience significant cognitive decline characterized by pronounced memory loss, impaired communication, and difficulties with executive functioning. They may struggle to remember recent events, find the right words in conversation, and make decisions or plan tasks. Behavioral changes such as agitation and mood swings become more frequent, while spatial awareness and orientation skills decline, leading to challenges in navigating familiar environments. Dependence on others for activities of daily living increases as judgment and reasoning abilities diminish. Personality changes may also occur, impacting the individual's previous traits. It's essential for caregivers and healthcare professionals to provide support and assistance tailored to the specific needs of individuals in this stage, focusing on maintaining dignity and quality of life."
        result = "Moderately Demented"
    elif result == "NonDemented":
        extra_details = "In Alzheimer's disease, a 'non-demented state' refers to individuals who, despite having Alzheimer's pathology, do not exhibit symptoms of dementia. This state suggests a degree of cognitive resilience or compensatory mechanisms that delay or prevent the onset of dementia symptoms. While Alzheimer's disease is characterized by the progressive accumulation of abnormal proteins in the brain, such as beta-amyloid plaques and tau tangles, not all affected individuals immediately develop dementia. Those in a non-demented state may still experience subtle cognitive changes, but these may not meet the criteria for clinical diagnosis. Understanding the factors contributing to cognitive resilience in Alzheimer's disease is crucial for developing interventions to delay or prevent dementia onset in susceptible individuals."
        result = "Non Demented"
    elif result == "VeryMildDemented":
        extra_details = "In the early stages of Alzheimer's disease, individuals may exhibit very mild cognitive decline characterized by subtle memory lapses, occasional confusion about time or place, mild difficulty with problem-solving tasks, and subtle changes in mood or personality. While these symptoms may be initially overlooked or attributed to normal aging, they represent the earliest signs of the progressive neurodegenerative disorder. Despite these cognitive changes, individuals with very mild Alzheimer's disease can typically maintain independence in daily activities, though they may benefit from medical evaluation, support services, and lifestyle interventions to manage symptoms and plan for the future. Early detection and intervention are crucial for accessing appropriate care and support and may help individuals and their families navigate the challenges associated with the disease."
        result = "Very Mildly Demented"
    else:
        extra_details = ""
        result = "Healthy!!"
        
    patient_info = [
        ["Patient Name:", patient_name],
        ["Age:", patient_age],
        ["Disease:", result],
    ]
    patient_table = Table(patient_info, colWidths=[100, 300])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(patient_table)

    elements.append(Paragraph("<br/><b>Additional Details:</b>", bold_style))
    elements.append(Paragraph(extra_details, normal_style))

    doc.build(elements)

    print(f"Medical report generated: {pdf_filename}")
    
@app.route('/admin')
def landing():
    return render_template('landing.html')


user_count = 8
def generate_user_id(name, age, location):
    try:
        # Get the current count of users
        admin_ref = db.reference('admin')
        user_count = admin_ref.child('user_count').get() or 0

        # Increment user count
        user_count += 1
        admin_ref.update({'user_count': user_count})

        # Generate user id with format "P000"
        user_id = "P{:03d}".format(user_count)

        # Add user details to the database
        admin_ref.child(user_id).set({
            'name': name,
            'age': age,
            'location': location
        })

        return user_id
    except Exception as e:
        print("Error:", e)
        return None




@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin_credential = db.reference('admin').get()
        name = "abc"
        pwd = "abc"
        if username == name and password == pwd:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('success'))
        
        error = 'Invalid username or password. Please try again.'
        return render_template('loginn.html', error=error)
    
    return render_template('login.html')

def delete_user(user_id):
    try:
        # Remove the user's entry from the database
        db.reference('admin').child(user_id).delete()
        return True
    except Exception as e:
        print("Error:", e)
        return False


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
        users = db.reference('admin').get()
    return render_template('dashboard.html', action=action, users=users)

@app.route('/dashboard/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        # Remove the specified user's entry from the database
        db.reference('admin').child(user_id).delete()
        return redirect(url_for('admin_dashboard', action='existing'))  # Redirect to existing users
    except Exception as e:
        print("Error:", e)
        # Handle error appropriately
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
