from flask import jsonify
from utils import validate_signup_form

def handle_register(request, collection):
    try:
        data = request.json
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        confirmpassword = data.get("confirmpassword")
        gender = data.get("gender")
        address = data.get("address")
        mobileno = data.get("mobileno")
        countrycode = data.get("countrycode")

        validation_error = validate_signup_form(username, password, confirmpassword, mobileno, countrycode)
        if validation_error:
            return jsonify({"status": "error", "message": validation_error}), 400

        if collection.find_one({"username": username}):
            return jsonify({"status": "error", "message": "Username already exists."}), 400
        if collection.find_one({"email": email}):
            return jsonify({"status": "error", "message": "Email already registered."}), 400

        user_data = {
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "email": email,
            "password": password,
            "gender": gender,
            "address": address,
            "mobileno": mobileno,
            "countrycode": countrycode,
        }
        collection.insert_one(user_data)
        return jsonify({"status": "success", "message": f"User {username} registered successfully!"})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
