from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
import random

app = Flask(__name__)
CORS(app)

# Secret key
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is not set!")

client = MongoClient(MONGO_URI)
db = client["aviation_db"]

users_col = db["users"]
flights_col = db["flights"]

# ---------------- Pages ----------------

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

@app.route("/map")
def map_page():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("map.html")

# ✅ THIS IS THE MISSING ROUTE
@app.route("/flights")
def flights_page():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("flights.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))

# ---------------- Auth API ----------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Invalid input"}), 400

    if users_col.find_one({"email": data["email"]}):
        return jsonify({"error": "User already exists"}), 400

    hashed = generate_password_hash(data["password"])
    users_col.insert_one({
        "email": data["email"],
        "password": hashed
    })
    return jsonify({"message": "Registered successfully"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = users_col.find_one({"email": data.get("email")})

    if not user or not check_password_hash(user["password"], data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user"] = user["email"]
    return jsonify({"message": "Logged in"})

# ---------------- Flights API ----------------

@app.route("/api/flights", methods=["GET"])
def get_flights():
    flights = list(flights_col.find({}, {"_id": 0}))
    return jsonify(flights)

@app.route("/api/flights", methods=["POST"])
def add_flight():
    data = request.json
    required = ["flight_no", "source", "destination", "status", "fuel"]

    if not data or not all(k in data for k in required):
        return jsonify({"error": "Invalid input"}), 400

    if flights_col.find_one({"flight_no": data["flight_no"]}):
        return jsonify({"error": "Flight already exists"}), 400

    data["fuel"] = int(data["fuel"])
    flights_col.insert_one(data)
    return jsonify({"message": "Flight added"})

@app.route("/api/flights", methods=["DELETE"])
def delete_flight():
    data = request.json
    if not data or "flight_no" not in data:
        return jsonify({"error": "Flight number required"}), 400

    result = flights_col.delete_one({"flight_no": data["flight_no"]})
    if result.deleted_count == 0:
        return jsonify({"error": "Flight not found"}), 404

    return jsonify({"message": "Flight deleted"})

@app.route("/api/simulate", methods=["POST"])
def simulate():
    flights = list(flights_col.find({}))
    for f in flights:
        new_status = random.choice(["On Time", "Delayed", "Boarding", "Departed"])
        new_fuel = max(0, f.get("fuel", 100) - random.randint(1, 10))

        flights_col.update_one(
            {"_id": f["_id"]},
            {"$set": {"status": new_status, "fuel": new_fuel}}
        )

    return jsonify({"message": "Simulation updated"})

# ---------------- Run ----------------

if __name__ == "__main__":
    app.run(debug=True)
