import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# ----------------------------------------
# 1. Load Data
# ----------------------------------------
train_df = pd.read_csv("../scrape/SPG/SPG_merged.csv")
test_df = pd.read_csv("../scrape/INVH/INVH_merged.csv")

print("Train Columns:", train_df.columns.tolist())
print("Test Columns:", test_df.columns.tolist())

print("\nTrain Missing Values:\n", train_df.isnull().sum())

# ----------------------------------------
# 2. Preprocessing
# ----------------------------------------

# Numeric Columns (Exclude REIT_Return since it's the target)
numeric_cols = [col for col in train_df.select_dtypes(include=[np.number]).columns if col != "REIT_Return"]

# Impute Missing
imputer = SimpleImputer(strategy='mean')
train_df[numeric_cols] = imputer.fit_transform(train_df[numeric_cols])
test_df[numeric_cols] = imputer.transform(test_df[numeric_cols])

# Classification Label based on train median
median_return = train_df["REIT_Return"].median()
train_df["REIT_Label"] = (train_df["REIT_Return"] > median_return).astype(int)

if "REIT_Return" in test_df.columns:
    test_df["REIT_Label"] = (test_df["REIT_Return"] > median_return).astype(int)

# ----------------------------------------
# 3. Regression Model (Predict REIT_Return)
# ----------------------------------------
X_train_reg = train_df[numeric_cols]
y_train_reg = train_df["REIT_Return"]

X_test_reg = test_df[numeric_cols]

scaler = StandardScaler()
X_train_reg_scaled = scaler.fit_transform(X_train_reg)
X_test_reg_scaled = scaler.transform(X_test_reg)

regressor = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
regressor.fit(X_train_reg_scaled, y_train_reg)

y_pred_reg = regressor.predict(X_test_reg_scaled)

# Only Evaluate MSE if REIT_Return exists
if "REIT_Return" in test_df.columns:
    y_test_reg = test_df["REIT_Return"]
    print("\n--- Regression Results ---")
    print(f"Mean Squared Error: {mean_squared_error(y_test_reg, y_pred_reg):.4f}")

# Plot Predictions
plt.figure(figsize=(12, 6))
plt.scatter(range(len(y_pred_reg)), y_pred_reg, alpha=0.5)
plt.xlabel('Sample')
plt.ylabel('Predicted Return')
plt.title('Predicted REIT Returns (INVH)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Feature Importance
importance_df = pd.DataFrame({
    "Feature": X_train_reg.columns,
    "Importance": regressor.feature_importances_
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 5))
plt.barh(importance_df["Feature"], importance_df["Importance"])
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance (Regressor)")
plt.tight_layout()
plt.show()

# ----------------------------------------
# 4. Classification Model (Predict REIT_Label)
# ----------------------------------------
X_train_class = X_train_reg
y_train_class = train_df["REIT_Label"]

X_test_class = X_test_reg

X_train_class_scaled = scaler.fit_transform(X_train_class)
X_test_class_scaled = scaler.transform(X_test_class)

classifier = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
classifier.fit(X_train_class_scaled, y_train_class)

y_pred_class = classifier.predict(X_test_class_scaled)

# Only Evaluate if REIT_Return exists
if "REIT_Label" in test_df.columns:
    y_test_class = test_df["REIT_Label"]
    print("\n--- Classification Results ---")
    print(f"Accuracy: {accuracy_score(y_test_class, y_pred_class) * 100:.2f}%")
    print(classification_report(y_test_class, y_pred_class))

# Feature Importance
importance_df = pd.DataFrame({
    "Feature": X_train_class.columns,
    "Importance": classifier.feature_importances_
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 5))
plt.barh(importance_df["Feature"], importance_df["Importance"])
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance (Classifier)")
plt.tight_layout()
plt.show()
