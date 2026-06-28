# CropAI — Crop Infection Prediction System

An ML-powered web platform that predicts crop infection risk from environmental and soil sensor data, helping farmers take preventive action before yield loss occurs.

🏆 **1st Prize — TinkerCase Hackathon, organized by IEEE**

---

## Overview

CropAI takes six field measurements — soil moisture, soil temperature, air temperature, air humidity, soil salinity, and NDVI (vegetation index) — and predicts an infection risk level on a scale of 1–10. Based on the predicted risk, it recommends suitable pesticides and lets users calculate exact dosage for their field size.

Built and demoed for wheat fields in Punjab, India, using a synthetically generated but domain-informed dataset.

## Features

- **Real-time prediction** — submit field readings and get an instant infection-risk score
- **Visual risk gauge** — live needle gauge showing risk level (low / medium / high)
- **Prediction history** — tracks past predictions with a trend chart
- **Pesticide recommendations** — risk-tiered suggestions (Neem Oil, Sulfur Dust, Copper Fungicide, etc.)
- **Dosage calculator** — scales pesticide quantity by field size (acres)
- **Model performance dashboard** — accuracy, precision, recall, F1 score

## Tech Stack

| Layer | Tech |
|---|---|
| ML Model | XGBoost Classifier |
| Data Processing | Pandas, NumPy, scikit-learn |
| Backend | Flask, Flask-CORS |
| Frontend | HTML, CSS, JavaScript, Chart.js |

## Project Structure

```
cropai/
├── app.py                          # Flask server + prediction API
├── model/
│   ├── sih.json                    # trained XGBoost model
│   └── scaler.pkl                  # fitted StandardScaler
├── data/
│   └── wheat_infection_punjab_5000.csv   # generated training dataset
├── scripts/
│   ├── dataset_for_sih.py          # synthetic dataset generator
│   └── sih_final_code.py           # model training (final version)
├── templates/
│   └── index.html                  # frontend UI
├── static/
│   ├── css/style.css
│   └── js/app.js
├── requirements.txt
└── README.md
```

## How the Model Works

1. **Dataset generation** (`scripts/dataset_for_sih.py`) simulates 5,000 realistic field readings for wheat crops, with infection levels derived from domain-informed thresholds (e.g. extreme soil moisture, high humidity, low NDVI all raise infection risk), then balances the dataset across all 10 risk levels.
2. **Model training** (`scripts/sih_final_code.py`) scales features with `StandardScaler` and trains an `XGBClassifier` (700 estimators, depth 7) to classify infection level (1–10).
3. **Serving** (`app.py`) loads the saved model and scaler, exposes a `/predict` endpoint, and maps predictions to a risk tier and pesticide recommendation.

## Running Locally

```bash
# 1. Clone the repo
git clone https://github.com/GITHUB_USERNAME/cropai.git
cd cropai

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Regenerate dataset and retrain model
python scripts/dataset_for_sih.py
python scripts/sih_final_code.py

# 4. Run the Flask app
python app.py
```

Then open `http://127.0.0.1:5001` in your browser.

## Future Improvements

- Replace synthetic dataset with real sensor/satellite data
- Add support for crops beyond wheat
- Persist prediction history server-side instead of in-browser memory
- Replace placeholder confidence score with calibrated model probabilities

---

Built by [Bhavansh Kapoor](https://github.com/GITHUB_USERNAME)
