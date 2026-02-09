from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
import random
import math
CITY_COORDS = {
    "chennai": (13.0827, 80.2707),
    "durgapur": (23.5204, 87.3119),
    "kolkata": (22.5726, 88.3639),
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
}

flight_routes = {}  # { flight_no: { "progress": 0.0 } }

app = Flask(__name__)
CORS(app)

# ------------------------
# Config
# ------------------------
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is not set!")

client = MongoClient(MONGO_URI)
db = client["aviation_db"]

users_col = db["users"]
flights_col = db["flights"]

# In-memory positions for live map
flight_positions = {}

# ------------------------
# Pages
# ------------------------

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

@app.route("/flights")
def flights_page():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("flights.html")

@app.route("/map")
def map_page():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template("map.html")

# ------------------------
# Auth API
# ------------------------

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

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))

# ------------------------
# Flights API
# ------------------------

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

    data["fuel"] = int(data["fuel"])
    flights_col.insert_one(data)
    return jsonify({"message": "Flight added"})

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

# ------------------------
# Live Map API
# ------------------------

@app.route("/api/flights/positions")
def flight_positions_api():
    flights = list(flights_col.find({}, {"_id": 0}))

    result = []

    for f in flights:
        fn = f["flight_no"]
        src = f["source"].lower()
        dst = f["destination"].lower()

        if src not in CITY_COORDS or dst not in CITY_COORDS:
            continue  # skip unknown cities

        lat1, lng1 = CITY_COORDS[src]
        lat2, lng2 = CITY_COORDS[dst]

        # Initialize route progress
        if fn not in flight_routes:
            flight_routes[fn] = {"progress": 0.0}

        # Move forward
        flight_routes[fn]["progress"] += 0.01  # speed
        if flight_routes[fn]["progress"] > 1.0:
            flight_routes[fn]["progress"] = 1.0  # stop at destination (or set 0.0 to loop)

        t = flight_routes[fn]["progress"]

        # Interpolate position
        lat = lat1 + (lat2 - lat1) * t
        lng = lng1 + (lng2 - lng1) * t

        result.append({
            "flight_no": fn,
            "lat": lat,
            "lng": lng,
            "status": f.get("status", "Unknown"),
            "fuel": f.get("fuel", 0),
            "src": src,
            "dst": dst,
            "src_coord": [lat1, lng1],
            "dst_coord": [lat2, lng2]
        })

    return jsonify(result)


# ------------------------
# Run
# ------------------------

if __name__ == "__main__":
    app.run(debug=True)
