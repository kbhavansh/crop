
import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Number of rows
n_samples = 5000

# Generate realistic ranges for Punjab wheat fields
soil_moisture = np.random.uniform(10, 60, n_samples)     # % moisture
soil_temp = np.random.uniform(5, 40, n_samples)          # °C
air_temp = np.random.uniform(5, 42, n_samples)           # °C
humidity = np.random.uniform(30, 95, n_samples)          # % humidity
salinity = np.random.uniform(0, 3, n_samples)            # dS/m
ndvi = np.random.uniform(0.2, 0.9, n_samples)            # NDVI vegetation index

# Infection scoring logic (realistic)
infection_score = (
    (soil_moisture < 20) * 2 +
    (soil_moisture > 50) * 2 +
    ((soil_temp < 10) | (soil_temp > 35)) * 2 +
    ((air_temp < 10) | (air_temp > 35)) * 2 +
    (humidity > 80) * 2 +
    (salinity > 1.5) * 2 +
    (ndvi < 0.4) * 3
).astype(float)

# Add continuous scaling for realism
infection_score += (
    (60 - soil_moisture) / 30 * 1.5 +
    (salinity * 1.5) +
    (1 - ndvi) * 3 +
    np.random.normal(0, 1, n_samples)   # noise
)

# Normalize infection score to range 1–10
infection_level = np.clip(np.round(
    1 + 9 * (infection_score - infection_score.min()) /
    (infection_score.max() - infection_score.min())
), 1, 10)

# Balance classes (force uniform distribution)
desired_count = n_samples // 10
balanced_indices = []
for lvl in range(1, 10 + 1):
    idx = np.where(infection_level == lvl)[0]
    if len(idx) >= desired_count:
        chosen = np.random.choice(idx, desired_count, replace=False)
    else:  # oversample if not enough
        chosen = np.random.choice(idx, desired_count, replace=True)
    balanced_indices.extend(chosen)

# Final balanced dataset
df = pd.DataFrame({
    "Soil_Moisture(%)": soil_moisture[balanced_indices],
    "Soil_Temp(C)": soil_temp[balanced_indices],
    "Air_Temperature(C)": air_temp[balanced_indices],
    "Air_Humidity(%)": humidity[balanced_indices],
    "Soil_Salinity(dS/m)": salinity[balanced_indices],
    "NDVI": ndvi[balanced_indices],
    "Infection_Level(1-10)": infection_level[balanced_indices]
})

# Save dataset
df.to_csv("data/wheat_infection_punjab_5000.csv", index=False)
print("✅ Dataset generated and saved as data/wheat_infection_punjab_5000.csv")
