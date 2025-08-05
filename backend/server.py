import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

# MongoDB Connection
mongo_uri = os.environ.get("MONGO_URI")
print("MONGO_URI from environment:", mongo_uri)  # Debugging line
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app, uri=mongo_uri)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "fallback-secret")
jwt = JWTManager(app)

users = mongo.db.users
transactions = mongo.db.transactions

# ---- Serve React Frontend ----
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    # Serve React build files or index.html for React Router
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

# Helper to convert ObjectId
def serialize(transaction):
    return {
        "id": str(transaction["_id"]),
        "type": transaction["type"],
        "category": transaction["category"],
        "amount": transaction["amount"],
        "date": transaction["date"],
        "note": transaction.get("note", "")
    }

# ---- AUTH ROUTES ----
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if users.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 400

    hashed_pw = generate_password_hash(password)
    users.insert_one({"username": username, "password": hashed_pw})

    return jsonify({"msg": "User registered successfully"}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"token": token}), 200

# ---- TRANSACTION ROUTES (Protected) ----
@app.route("/api/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    all_txns = transactions.find({"user_id": user_id})
    return jsonify([serialize(t) for t in all_txns])

@app.route("/api/transactions", methods=["POST"])
@jwt_required()
def add_transaction():
    user_id = get_jwt_identity()
    data = request.json
    required_fields = ["type", "category", "amount"]

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    txn = {
        "user_id": user_id,
        "type": data["type"],
        "category": data["category"],
        "amount": float(data["amount"]),
        "date": data.get("date", datetime.utcnow().isoformat()),
        "note": data.get("note", "")
    }
    result = transactions.insert_one(txn)
    inserted_txn = transactions.find_one({"_id": result.inserted_id})
    return jsonify(serialize(inserted_txn)), 201

@app.route("/api/transactions/<id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(id):
    user_id = get_jwt_identity()
    result = transactions.delete_one({"_id": ObjectId(id), "user_id": user_id})
    if result.deleted_count == 1:
        return jsonify({"msg": "Deleted"}), 200
    return jsonify({"msg": "Not found"}), 404

@app.route("/api/transactions/<id>", methods=["PUT"])
@jwt_required()
def update_transaction(id):
    user_id = get_jwt_identity()
    data = request.json
    result = transactions.update_one(
        {"_id": ObjectId(id), "user_id": user_id},
        {"$set": {
            "type": data["type"],
            "category": data["category"],
            "amount": float(data["amount"]),
            "date": data.get("date", datetime.utcnow().isoformat()),
            "note": data.get("note", "")
        }}
    )
    if result.matched_count:
        return jsonify({"msg": "Updated"}), 200
    return jsonify({"msg": "Not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
