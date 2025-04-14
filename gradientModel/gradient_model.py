import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# ------------------------------
# 1. Load and Prepare Data
# ------------------------------
train_df = pd.read_csv("../scrape/SPG/SPG_merged.csv")
test_df = pd.read_csv("../scrape/INVH/")

# First, let's check what columns we actually have
print("Available columns in the DataFrame:", df.columns.tolist())
print("\nMissing values per column:")
print(df.isnull().sum())

# Create REIT_Label column based on whether return is above the median
df["REIT_Label"] = (df["REIT_Return"] > df["REIT_Return"].median()).astype(int)

# ------------------------------
# 2. Handle Missing Values
# ------------------------------
# Option 1: Drop rows with missing values
# df = df.dropna()

# Option 2: Impute missing values (better)
imputer = SimpleImputer(strategy='mean')  # can also use 'median' or 'most_frequent'
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

# ------------------------------
# 3. Regression Model (Continuous Target)
# ------------------------------
# Separate features and target - use only numeric columns
X = df[numeric_cols].drop(columns=["REIT_Return", "REIT_Label"])
y_reg = df["REIT_Return"]

# Split the data -- CAUSING THE PROBLEM!!!
X_train, X_test, y_train, y_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)

# Standardize the data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the Gradient Boosting model (for regression)
gb_regressor = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gb_regressor.fit(X_train_scaled, y_train)

# Predict on the test set
y_pred_reg = gb_regressor.predict(X_test_scaled)

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
plt.tight_layout()
plt.show()

# ------------------------------
# 4. Plot Actual vs Predicted
# ------------------------------
plt.figure(figsize=(12, 6))
plt.scatter(y_test, y_pred_reg, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
plt.xlabel('Actual Returns')
plt.ylabel('Predicted Returns')
plt.title('Actual vs Predicted REIT Returns')
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------
# 5. Classification Model (Categorical Target)
# ------------------------------
# Use the categorical label as the target
y_class = df["REIT_Label"]

# Split the data (using same split as regression for consistency)
X_train, X_test, y_train, y_test = train_test_split(X, y_class, test_size=0.2, random_state=42)

# Standardize the data
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the Gradient Boosting model (for classification)
gb_classifier = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gb_classifier.fit(X_train_scaled, y_train)

# Predict on the test set
y_pred_class = gb_classifier.predict(X_test_scaled)

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
plt.tight_layout()
plt.show()