import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import xgboost as xgb  # ✅ NEW

# ----------------------------------------
# 1. Load Data
# ----------------------------------------
train_df = pd.read_csv("../scrape/SPG/SPG_merged.csv")
test_df = pd.read_csv("../scrape/INVH/INVH_merged.csv")

print("Train Columns:", train_df.columns.tolist())
print("Test Columns:", test_df.columns.tolist())
print("\nMissing values in {train_df}:\n", train_df.isnull().sum())
print("\nMissing values in {test_df}:\n", test_df.isnull().sum())

# ----------------------------------------
# 2. Preprocessing
# ----------------------------------------
numeric_cols = [col for col in train_df.select_dtypes(include=[np.number]).columns if col != "REIT_Return"]

#Add data analysis
print("\n--- Data Analysis ---")
print("Target Variable (REIT_Return) Statistics:")
print(train_df["REIT_Return"].describe())
print("\nFeature Statistics:")
print(train_df.describe)
print(train_df[numeric_cols].describe())

imputer = SimpleImputer(strategy='mean')
train_df[numeric_cols] = imputer.fit_transform(train_df[numeric_cols])
test_df[numeric_cols] = imputer.transform(test_df[numeric_cols])

# Add feature engineering
train_df['profit_margin'] = train_df['netincome'] / train_df['revenue']
test_df['profit_margin'] = test_df['netincome'] / test_df['revenue']

train_df['asset_turnover'] = train_df['revenue'] / train_df['assets']
test_df['asset_turnover'] = test_df['revenue'] / test_df['assets']

# Update numeric columns to include new features
numeric_cols.extend(['profit_margin', 'asset_turnover'])

median_return = train_df["REIT_Return"].median()
train_df["REIT_Label"] = (train_df["REIT_Return"] > median_return).astype(int)

if "REIT_Return" in test_df.columns:
    test_df["REIT_Label"] = (test_df["REIT_Return"] > median_return).astype(int)

# ----------------------------------------
# 3. Regression Model (XGBoost Regressor)
# ----------------------------------------
X_train_reg = train_df[numeric_cols]
y_train_reg = train_df["REIT_Return"]
X_test_reg = test_df[numeric_cols]

scaler = StandardScaler()
X_train_reg_scaled = scaler.fit_transform(X_train_reg)
X_test_reg_scaled = scaler.transform(X_test_reg)

# Updated model parameters for more aggressive learning
regressor = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.05,  # Increased from 0.01
    max_depth=5,         # Increased from 3
    min_child_weight=1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
regressor.fit(X_train_reg_scaled, y_train_reg)

y_pred_reg = regressor.predict(X_test_reg_scaled)

# Enhanced analysis of predictions
print("\n--- Enhanced Prediction Analysis ---")
analysis_df = test_df.copy()
analysis_df['predicted_return'] = y_pred_reg
analysis_df['prediction_group'] = ['high' if x > np.median(y_pred_reg) else 'low' for x in y_pred_reg]

# Time-based analysis
print("\nTime-based Statistics:")
analysis_df['date'] = pd.to_datetime(analysis_df['date'])
analysis_df['year'] = analysis_df['date'].dt.year
yearly_stats = analysis_df.groupby('year')['predicted_return'].agg(['mean', 'std', 'count'])
print("\nYearly Prediction Statistics:")
print(yearly_stats)

# Feature correlation with predictions
print("\nFeature Correlation with Predicted Returns:")
correlations = {}
for col in numeric_cols:
    if col in analysis_df.columns:
        correlation = analysis_df[col].corr(analysis_df['predicted_return'])
        correlations[col] = correlation

# Sort and print correlations
sorted_correlations = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
print("\nTop Feature Correlations with Predicted Returns:")
for feature, corr in sorted_correlations[:5]:
    print(f"{feature}: {corr:.3f}")

# Group statistics
print("\nKey Metrics by Prediction Group:")
for col in sorted_correlations[:5]:  # Top 5 correlated features
    feature = col[0]
    if feature in analysis_df.columns:
        group_stats = analysis_df.groupby('prediction_group')[feature].agg(['mean', 'median', 'std'])
        print(f"\n{feature}:")
        print(group_stats)

# Print regression predictions
print("\n--- Regression Predictions ---")
print("First 10 predicted returns:")
for i, pred in enumerate(y_pred_reg[:10]):
    print(f"Sample {i+1}: {pred:.4f}")

if "REIT_Return" in test_df.columns:
    y_test_reg = test_df["REIT_Return"]
    print("\n--- Regression Results ---")
    print(f"Mean Squared Error: {mean_squared_error(y_test_reg, y_pred_reg):.4f}")

# Plot predictions
plt.figure(figsize=(12, 6))
plt.scatter(range(len(y_pred_reg)), y_pred_reg, alpha=0.5)
plt.xlabel('Sample')
plt.ylabel('Predicted Return')
plt.title('Predicted REIT Returns (INVH)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Feature importance (regression)
importance_df = pd.DataFrame({
    "Feature": X_train_reg.columns,
    "Importance": regressor.feature_importances_
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 5))
plt.barh(importance_df["Feature"], importance_df["Importance"])
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance (XGBoost Regressor)")
plt.tight_layout()
plt.show()

# ----------------------------------------
# 4. Classification Model (XGBoost Classifier)
# ----------------------------------------
X_train_class = X_train_reg
y_train_class = train_df["REIT_Label"]
X_test_class = X_test_reg

X_train_class_scaled = scaler.fit_transform(X_train_class)
X_test_class_scaled = scaler.transform(X_test_class)

# Updated classifier parameters
classifier = xgb.XGBClassifier(
    n_estimators=200,     # Increased from 100
    learning_rate=0.1,
    max_depth=5,         # Increased from 3
    min_child_weight=1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
classifier.fit(X_train_class_scaled, y_train_class)

y_pred_class = classifier.predict(X_test_class_scaled)

# Print classification predictions
print("\n--- Classification Predictions ---")
print("First 10 predicted labels:")
for i, pred in enumerate(y_pred_class[:10]):
    print(f"Sample {i+1}: {'Above Median' if pred == 1 else 'Below Median'}")

if "REIT_Label" in test_df.columns:
    y_test_class = test_df["REIT_Label"]
    print("\n--- Classification Results ---")
    print(f"Accuracy: {accuracy_score(y_test_class, y_pred_class) * 100:.2f}%")
    print(classification_report(y_test_class, y_pred_class))

# Feature importance (classification)
importance_df = pd.DataFrame({
    "Feature": X_train_class.columns,
    "Importance": classifier.feature_importances_
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 5))
plt.barh(importance_df["Feature"], importance_df["Importance"])
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance (XGBoost Classifier)")
plt.tight_layout()
plt.show()
