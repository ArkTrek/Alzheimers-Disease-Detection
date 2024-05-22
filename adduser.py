import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK with credentials
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://alzheimerdetectionsystem-default-rtdb.firebaseio.com/'
})


# Function to store user data
def store_user_data(user_id, user_data):
    ref = db.reference('users/' + user_id)
    ref.set(user_data)

# Sample user data
user1_data = {
    'name': 'Ashwanth',
    'pwd': 'asd123',
    'Desc':'NonDemented',
    'admin': False
}

user2_data = {
    'name': 'ash',
    'pwd': 'abc12',
    'admin': True
}

# Store user data
store_user_data(user1_data['name'], user1_data)
store_user_data(user2_data['name'], user2_data)

print("User data stored successfully.")
