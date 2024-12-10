import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import base64
from flask import Flask, render_template, request, redirect, url_for
from register import handle_register
import re
from flask import jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi


app = Flask(__name__)

# MongoDB Connection
def connect_to_mongodb(uri):
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        print("Connected to MongoDB successfully!")
        return client
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# MongoDB URI
MONGO_URI = "mongodb+srv://adi:plantdisease@cluster0.1wwnm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = connect_to_mongodb(MONGO_URI)
if client:
    try:
        client.admin.command('ping')
        print("Pinged your deployment. Successfully connected to MongoDB!")
    except Exception as e:
        print(e)

# Select Database and Collection
db = client.adi  # Replace with your database name
collection = db.Signed_User  # Replace with your collection name


# Load the TFLite model and allocate tensors
def load_tflite_model(model_path):
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

# Load the TFLite model
interpreter = load_tflite_model('saved_models/Disease_Classifier.tflite')

class_names = [
    'Apple Black Rot', 'Apple Scab', 'Blueberry Healthy', 'Cedar Apple', 'Cherry Healthy', 'Cherry Powdery Mildew',
    'Corn (maize) Cercospora leaf spot', 'Corn (maize) Healthy', 'Corn (maize) Northern Leaf Blight', 'Corn (maize) Rust',
    'Grape Black Measles', 'Grape Black Rot', 'Grape Healthy', 'Grape Leaf Blight', 'Healthy Apple', 'Orange Black Spot',
    'Orange Canker', 'Orange Fresh', 'Orange Grenning', 'Orange Haunglongbing', 'Peach Bacterial Spot', 'Peach Healthy',
    'Pepper Bell Bacterial Spot', 'Pepper Bell Healthy', 'Potato Early Blight', 'Potato Healthy', 'Potato Late Blight',
    'Raspberry Healthy', 'Rice Bacterial Blight', 'Rice Blast', 'Rice Brownspot', 'Rice Tungro', 'Soybean Healthy',
    'Squash Powdery Mildew', 'Strawberry Healthy', 'Strawberry Leaf Scorch', 'Sugarcane Healthy', 'Sugarcane Mosaic',
    'Sugarcane RedRot', 'Sugarcane Rust', 'Sugarcane Yellow', 'Tomato Bacterial Spot', 'Tomato Early Blight', 'Tomato Healthy',
    'Tomato Late Blight', 'Tomato Leaf Mold', 'Tomato Mosaic Virus', 'Tomato Septoria Leaf Spot', 'Tomato Spider Mites',
    'Tomato Target Spot', 'Tomato Yellow Leaf Curl Virus'
]

def predict(interpreter, img):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    img = img.resize((128, 128))  # Resize image to match model input size
    img_array = np.expand_dims(np.array(img), axis=0).astype(np.float32)

    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    predicted_class = class_names[np.argmax(output_data[0])]
    confidence = round(100 * np.max(output_data[0]), 2)
    return predicted_class, confidence

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            img = Image.open(BytesIO(file.read()))
            predicted_class, confidence = predict(interpreter, img)
            img_data = BytesIO()
            img.save(img_data, format='PNG')
            img_data.seek(0)
            img_base64 = base64.b64encode(img_data.getvalue()).decode('utf-8')
            return render_template(
                'result.html',
                img_data=img_base64,
                class_name=predicted_class,
                confidence=confidence
            )
    # Render fresh page on GET requests
    return render_template('index.html')

# Helper Function: Validate Form Fields
def validate_signup_form(username, password, confirmpassword, mobileno, countrycode):
    print("-"*20, "Validating Signup Form Fields", "-"*20)
    # Username: At least 4 characters
    if len(username) < 4:
        return "Username must be at least 4 characters long."

    # Password: At least 8 characters with 1 symbol, 1 digit, 1 alphabet
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[^\w\s]', password):
        return "Password must be at least 8 characters long, with 1 letter, 1 digit, and 1 symbol."

    # Confirm Password
    if password != confirmpassword:
        return "Passwords do not match."

    # Mobile Number Validation by Country
    if countrycode == "+91" and len(mobileno) != 10:  # India
        return "Mobile number for India must be 10 digits."
    elif countrycode == "+1" and len(mobileno) != 10:  # US
        return "Mobile number for US must be 10 digits."
    elif countrycode == "+44" and len(mobileno) != 11:  # UK
        return "Mobile number for UK must be 11 digits."

    # All validations passed
    return None

@app.route('/contactUs')
def contact_us():
    return render_template('/contactUs.html')

@app.route('/aboutUs')
def about_us():
    return render_template('aboutus.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_val():
    try:
        print("-"*20, "Logging In User", "-"*20)
        # Ensure the content type is JSON
        if request.content_type != 'application/json':
            return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

        # Parse JSON data from the request
        data = request.json
        username = data.get("username")
        password = data.get("password")

        # Query MongoDB to find the user with the matching username and password
        user = collection.find_one({"username": username, "password": password})
        
        if user:
            return jsonify({"status": "success", "message": "Login successful!"})
        else:
            return jsonify({"status": "error", "message": "Invalid username or password."}), 401

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500



@app.route("/register.py", methods=["POST"])
def register():
    return handle_register(request, collection)


if __name__ == '__main__':
    app.run(debug=True)