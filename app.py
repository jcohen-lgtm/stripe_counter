import os
import stripe
from flask import Flask, jsonify

app = Flask(__name__)

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

@app.route("/")
def home():
    return "Stripe Counter is running"

@app.route("/stats")
def stats():
    try:
        customers = stripe.Customer.list(limit=100)
        return jsonify({
            "total_customers": len(customers.data)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
