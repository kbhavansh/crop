# Step 1: Import libraries
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import pandas as pd
import joblib
import os

# Step 2: Load dataset
csv_path = "data/wheat_infection_punjab_5000.csv"
df = pd.read_csv(csv_path)

# Strip spaces in column names
df.columns = df.columns.str.strip()

# Step 3: Features and target
X = df.drop(columns=['Infection_Level(1-10)'])
y = df['Infection_Level(1-10)'] - 1   # shift 1–10 → 0–9

# Step 4: Feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 5: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Step 6: Train XGBoost Classifier
model = xgb.XGBClassifier(
    n_estimators=700,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    gamma=1,
    reg_alpha=0.1,
    reg_lambda=1.0,
    objective='multi:softprob',
    num_class=len(y.unique()),
    eval_metric="mlogloss",
    random_state=42,
    use_label_encoder=False
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

# Step 7: Evaluate model
y_pred = model.predict(X_test)

# Convert back to 1–10 levels
y_pred_display = y_pred + 1
y_test_display = y_test + 1

# Exact accuracy
accuracy = accuracy_score(y_test, y_pred)
print("✅ XGBoost Classification Accuracy:", round(accuracy, 3))

# ±1 tolerance accuracy
tolerable_accuracy = ((abs(y_pred_display - y_test_display) <= 1).sum()) / len(y_test)
print("✅ ±1 Infection Level Accuracy:", round(tolerable_accuracy, 3))

# Step 8: Dataset balance check
print("\n📊 Dataset Distribution (1–10 infection levels):")
print(df['Infection_Level(1-10)'].value_counts().sort_index())

# Step 9: Test prediction with realistic inputs
print("\n🌾 Predicting Infection Level for realistic wheat conditions...")
realistic_inputs = {
    'Soil_Moisture(%)': 30.0,
    'Soil_Temp(C)': 22.0,
    'Air_Temperature(C)': 26.0,
    'Air_Humidity(%)': 65.0,
    'Soil_Salinity(dS/m)': 1.2,
    'NDVI': 0.70
}
sample = pd.DataFrame([realistic_inputs])
sample_scaled = scaler.transform(sample)

prediction = model.predict(sample_scaled)[0]
infection_level = int(prediction) + 1   # ✅ shifted back
print("👉 Predicted Infection Level:", infection_level)

# Step 10: Save model and scaler
os.makedirs("model", exist_ok=True)
model.save_model("model/sih.json")
joblib.dump(scaler, "model/scaler.pkl")
print("\n💾 Model saved to model/sih.json")
print("💾 Scaler saved to model/scaler.pkl")
