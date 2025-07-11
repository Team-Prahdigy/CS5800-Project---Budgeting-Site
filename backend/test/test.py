import unittest
import sys
import os
import importlib.util

# Import your server module properly
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server.py'))
spec = importlib.util.spec_from_file_location("server_module", app_path)
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)

app = server_module.app
mongo = server_module.mongo

from flask.testing import FlaskClient

class TransactionAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client: FlaskClient = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        self.mongo = mongo
        self.db = mongo.db
        self.db.transactions.delete_many({})  # Clean collection before each test

    def tearDown(self):
        self.db.transactions.delete_many({})
        # Do NOT close the mongo client here, it will cause errors in further tests
        # self.mongo.cx.close()
        self.app_context.pop()

    def test_create_transaction_success(self):
        """Test creating a valid transaction"""
        transaction = {
            "type": "income",
            "category": "Salary",
            "amount": 5000,
            "note": "July paycheck"
        }
        response = self.client.post("/api/transactions", json=transaction)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("id", data)  # Check for "id", not "_id"

    def test_create_transaction_missing_field(self):
        """Test creating a transaction missing required field (amount)"""
        transaction = {
            "type": "expense",
            "category": "Rent"
            # 'amount' is intentionally missing
        }
        response = self.client.post("/api/transactions", json=transaction)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()
