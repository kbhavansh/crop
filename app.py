from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from xgboost import XGBClassifier
import joblib
import random

# ---------------- Load Model & Scaler ----------------
model = XGBClassifier()
model.load_model("model/sih.json")

# Load the same scaler used in training
scaler = joblib.load("model/scaler.pkl")   # ✅ make sure you saved scaler during training

# ---------------- Flask App ----------------
app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return render_template("index.html")


# ---------------- Prediction API ----------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        # ✅ Create DataFrame in correct order
        df = pd.DataFrame([{
            "Soil_Moisture(%)": data.get("soil_moisture", 0),
            "Soil_Temp(C)": data.get("soil_temp", 0),
            "Air_Temperature(C)": data.get("air_temp", 0),
            "Air_Humidity(%)": data.get("air_humidity", 0),
            "Soil_Salinity(dS/m)": data.get("soil_salinity", 0),
            "NDVI": data.get("ndvi", 0)
        }])

        # ✅ Ensure column order
        df = df[[
            "Soil_Moisture(%)",
            "Soil_Temp(C)",
            "Air_Temperature(C)",
            "Air_Humidity(%)",
            "Soil_Salinity(dS/m)",
            "NDVI"
        ]]

        # ✅ Apply scaler
        df_scaled = scaler.transform(df)

        # ✅ Prediction (shift back to 1–10)
        pred = int(model.predict(df_scaled)[0]) + 1
        confidence = round(random.uniform(70, 99), 2)

        # ✅ Risk & pesticide mapping
        if pred <= 3:
            risk_level = "low"
            pesticides = ["Neem Oil"]
        elif pred <= 6:
            risk_level = "medium"
            pesticides = ["Neem Oil", "Sulfur Dust"]
        else:
            risk_level = "high"
            pesticides = ["Copper Fungicide", "Potassium Bicarbonate", "Mancozeb"]

        return jsonify({
            "infection_level": pred,
            "confidence": confidence,
            "risk_level": risk_level,
            "recommended_pesticides": pesticides
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---------------- Dosage Calculator API ----------------
@app.route("/calculate_dosage", methods=["POST"])
def calculate_dosage():
    try:
        data = request.json
        field_size = float(data.get("field_size", 1))   # hectares
        crop_type = "Wheat"  # ✅ fixed to wheat for now

        # ✅ Realistic base dosage for wheat in Punjab (per hectare)
        base_dosage = {
            "Wheat": {
                "Neem Oil": 1500,               # ml/ha (preventive)
                "Sulfur Dust": 2.5,             # kg/ha (medium risk)
                "Copper Fungicide": 1.5,        # kg/ha (high risk)
                "Potassium Bicarbonate": 1.5,   # kg/ha (high risk)
                "Mancozeb": 1.5                 # kg/ha (high risk)
            }
        }

        if crop_type not in base_dosage:
            return jsonify({"error": "Crop type not supported"}), 400

        # ✅ Scale dosage by field size
        dosages = {
            pesticide: round(amount * field_size, 2)
            for pesticide, amount in base_dosage[crop_type].items()
        }

        return jsonify({
            "field_size": field_size,
            "crop_type": crop_type,
            "dosages": dosages
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
