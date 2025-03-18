import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

# ------------------------------
# 1. Generate Mock Data
# ------------------------------
np.random.seed(42)

# Simulate features
n_samples = 1000
data = {
    "Interest_Rate": np.random.uniform(1.5, 5.5, n_samples),     # Interest rates between 1.5% and 5.5%
    "Inflation": np.random.uniform(1.0, 4.0, n_samples),          # Inflation rates between 1% and 4%
    "GDP_Growth": np.random.uniform(-2, 5, n_samples),            # GDP growth between -2% and 5%
    "Debt_to_Equity": np.random.uniform(0.5, 2.5, n_samples),     # Debt-to-equity ratio
    "Dividend_Yield": np.random.uniform(2.0, 8.0, n_samples),     # Dividend yield between 2% and 8%
    "Occupancy_Rate": np.random.uniform(60, 100, n_samples)       # Occupancy rate between 60% and 100%
}

# Create DataFrame
df = pd.DataFrame(data)

# Add a continuous target for regression
df["REIT_Returns"] = (
    0.02 * df["Interest_Rate"] - 
    0.01 * df["Inflation"] + 
    0.03 * df["GDP_Growth"] + 
    0.01 * df["Dividend_Yield"] + 
    np.random.normal(0, 0.5, n_samples)
)

# Add a categorical target for classification
df["REIT_Label"] = np.where(df["REIT_Returns"] > df["REIT_Returns"].median(), 1, 0)

# ------------------------------
# 2. Regression Model (Continuous Target)
# ------------------------------
# Separate features and target
X = df.drop(columns=["REIT_Returns", "REIT_Label"])
y_reg = df["REIT_Returns"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)

# Standardize the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train the Gradient Boosting model (for regression)
gb_regressor = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gb_regressor.fit(X_train, y_train)

# Predict on the test set
y_pred_reg = gb_regressor.predict(X_test)

# Evaluate model performance
mse = mean_squared_error(y_test, y_pred_reg)
print("\n--- Regression Results ---")
print(f"Mean Squared Error: {mse:.4f}")

# Plot feature importance
feature_importance = gb_regressor.feature_importances_
importance_df = pd.DataFrame({"Feature": X.columns, "Importance": feature_importance})
importance_df = importance_df.sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 5))
plt.barh(importance_df["Feature"], importance_df["Importance"])
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance in Gradient Boosting Regressor")
plt.show()

# ------------------------------
# 3. Get Prediction for a Real REIT (Using New Data)
# ------------------------------
# Example: new REIT data
new_data = {
    "Interest_Rate": [4.2],        # Interest rate for the REIT
    "Inflation": [3.1],             # Inflation rate for the REIT
    "GDP_Growth": [2.5],            # GDP growth for the REIT
    "Debt_to_Equity": [1.8],        # Debt-to-equity ratio for the REIT
    "Dividend_Yield": [5.4],        # Dividend yield for the REIT
    "Occupancy_Rate": [90.0]        # Occupancy rate for the REIT
}

# Convert new data into DataFrame for compatibility with the model
new_data_df = pd.DataFrame(new_data)

# Standardize the new data (using the same scaler as used for training)
new_data_scaled = scaler.transform(new_data_df)

# Get the prediction for REIT return
predicted_reit_return = gb_regressor.predict(new_data_scaled)

# Print the predicted REIT return
print(f"\nPredicted REIT Return: {predicted_reit_return[0]:.4f}")

# ------------------------------
# 4. Classification Model (Categorical Target)
# ------------------------------
# Use the categorical label as the target
y_class = df["REIT_Label"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.2, random_state=42)

# Train the Gradient Boosting model (for classification)
gb_classifier = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gb_classifier.fit(X_train, y_train)

# Predict on the test set
y_pred_class = gb_classifier.predict(X_test)

# Evaluate model performance
accuracy = accuracy_score(y_test, y_pred_class)
print("\n--- Classification Results ---")
print(f"Accuracy: {accuracy * 100:.2f}%")
print(classification_report(y_test, y_pred_class))

# Plot feature importance
feature_importance = gb_classifier.feature_importances_
importance_df = pd.DataFrame({"Feature": X.columns, "Importance": feature_importance})
importance_df = importance_df.sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 5))
plt.barh(importance_df["Feature"], importance_df["Importance"])
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance in Gradient Boosting Classifier")
plt.show()