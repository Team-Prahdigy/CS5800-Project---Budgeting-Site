import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

#For local development, use the local MongoDB instance below
# MongoDB connection
#app.config["MONGO_URI"] = "mongodb+srv://admin:admin@budgetapp.l9ol73l.mongodb.net/budgetapp?retryWrites=true&w=majority&appName=budgetapp"

#For production, use the MongoDB Atlas connection below
print("MONGO_URI from environment:", os.environ.get("MONGO_URI")) # Debugging line to check if MONGO_URI is set
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)
transactions = mongo.db.transactions

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

# GET all transactions
@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    all_txns = transactions.find()
    return jsonify([serialize(t) for t in all_txns])

# POST a new transaction
@app.route("/api/transactions", methods=["POST"])
def add_transaction():
    data = request.json
    required_fields = ["type", "category", "amount"]

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    txn = {
        "type": data["type"],  # "income" or "expense"
        "category": data["category"],
        "amount": float(data["amount"]),
        "date": data.get("date", datetime.utcnow().isoformat()),
        "note": data.get("note", "")
    }
    result = transactions.insert_one(txn)
    inserted_txn = transactions.find_one({"_id": result.inserted_id})

    # Return full serialized response with "id" field
    return jsonify(serialize(inserted_txn)), 201

# DELETE a transaction
@app.route("/api/transactions/<id>", methods=["DELETE"])
def delete_transaction(id):
    result = transactions.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({"msg": "Deleted"}), 200
    return jsonify({"msg": "Not found"}), 404

# PUT (update) a transaction
@app.route("/api/transactions/<id>", methods=["PUT"])
def update_transaction(id):
    data = request.json
    result = transactions.update_one(
        {"_id": ObjectId(id)},
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
