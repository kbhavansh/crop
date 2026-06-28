# Step 1: Import libraries
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Step 2: Load dataset
csv_path = "data/wheat_infection_punjab_5000.csv"
df = pd.read_csv(csv_path)

# Features and target
X = df.drop(columns=['Infection_Level(1-10)'])
y = df['Infection_Level(1-10)']

# Feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 3: Train-Test-Validation Split
X_train, X_temp, y_train, y_temp = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

# Step 4: Train XGBoost Regressor
model = xgb.XGBRegressor(
    n_estimators=800,
    max_depth=6,
    learning_rate=0.03,
    subsample=0.85,
    colsample_bytree=0.85,
    gamma=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    objective='reg:squarederror',
    random_state=42
)

model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=False
)

# -----------------------------
# Step 5: Evaluation
# -----------------------------
y_pred_cont = model.predict(X_test)
y_pred_rounded = np.clip(np.round(y_pred_cont), 1, 10)

r2 = r2_score(y_test, y_pred_cont)
mse = mean_squared_error(y_test, y_pred_cont)
rmse = np.sqrt(mse)
acc = accuracy_score(y_test, y_pred_rounded)

print("✅ Improved Model Results on Realistic Dataset:")
print(f"R² Score: {r2:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"Rounded Accuracy (exact infection level match): {acc:.3f}")

# Confusion Matrix for rounded predictions
cm = confusion_matrix(y_test, y_pred_rounded)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=range(1, 11),
            yticklabels=range(1, 11))
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix (Rounded Predictions)")
plt.show()

# -----------------------------
# Step 6: Realistic predefined values for testing
# -----------------------------
print("\n🌾 Predicting Infection Level for realistic wheat conditions...")

realistic_inputs = {
    'Soil_Moisture(%)': 28.0,     # Ideal 25–35%
    'Soil_Salinity(dS/m)': 2.1,   # Ideal < 4
    'NDVI': 0.65,                 # Healthy crop ~0.6–0.8
    'Air_Temperature(C)': 25.0,   # Ideal ~20–30 °C
    'Air_Humidity(%)': 60.0       # Moderate ~55–70%
}

sample = pd.DataFrame([realistic_inputs])
sample_scaled = scaler.transform(sample)

prediction_cont = model.predict(sample_scaled)[0]
prediction_level = int(np.clip(round(prediction_cont), 1, 10))

print(f"🎯 Predicted Infection Level: {prediction_level}")
