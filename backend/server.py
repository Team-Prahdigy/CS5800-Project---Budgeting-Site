import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

mongo_uri = os.environ.get("MONGO_URI")
print("MONGO_URI from environment:", mongo_uri)
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app, uri=mongo_uri)

transactions = mongo.db.transactions

# ------------------ API ROUTES ------------------

def serialize(transaction):
    return {
        "id": str(transaction["_id"]),
        "type": transaction["type"],
        "category": transaction["category"],
        "amount": transaction["amount"],
        "date": transaction["date"],
        "note": transaction.get("note", "")
    }

@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    all_txns = transactions.find()
    return jsonify([serialize(t) for t in all_txns])

@app.route("/api/transactions", methods=["POST"])
def add_transaction():
    data = request.json
    required_fields = ["type", "category", "amount"]

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    txn = {
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
def delete_transaction(id):
    result = transactions.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({"msg": "Deleted"}), 200
    return jsonify({"msg": "Not found"}), 404

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

# ------------------ SERVE REACT FRONTEND ------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True)
