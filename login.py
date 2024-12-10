from flask import jsonify

def handle_login(request, collection):
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        user = collection.find_one({"username": username, "password": password})
        if user:
            return jsonify({"status": "success", "message": "Login successful!"})
        else:
            return jsonify({"status": "error", "message": "Invalid username or password."}), 401

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500
