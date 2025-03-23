# Gradient Boosting Model Documentation

## Overview
Gradient Boosting is an ensemble machine learning technique that builds a strong predictive model by combining multiple weak models (usually decision trees). The idea behind gradient boosting is to fit a new model to the residual errors of the previous models, effectively correcting the mistakes made by earlier models.

### Key Features:
- **Ensemble Learning**: Combines predictions from multiple models (weak learners) to improve accuracy.
- **Boosting**: Iteratively corrects errors made by earlier models in the sequence.
- **Gradient Descent**: Uses gradient descent to minimize the loss function by fitting new models to the residual errors of the ensemble.

---

## Data Types

### Feature Importance
- **Definition**: Feature importance refers to how much each feature contributes to the predictive power of the model.
- **Role in Gradient Boosting**: In Gradient Boosting, each feature is assessed during the construction of the trees, and their importance is calculated based on how much each feature reduces the model’s prediction error.

### Residuals
- **Definition**: Residuals are the errors made by the model in its predictions.
- **Role in Gradient Boosting**: In each boosting iteration, a new decision tree is trained to predict the residuals from the previous model, thus correcting the model’s predictions.

---

## Model Structure

### Weak Learners (Decision Trees)
- **Purpose**: The base model used in Gradient Boosting is typically a decision tree, which is considered a weak learner.
- **Why Decision Trees?**: Decision trees are chosen because they can handle both numerical and categorical data and are easy to interpret.
- **Tree Growth**: Trees are built iteratively, and at each stage, a new tree is trained to correct the residual errors of the previous trees.

### Boosting Algorithm
- **Purpose**: The boosting algorithm sequentially adds new trees that improve the performance of the model by correcting the errors of the previous trees.
- **How It Works**: 
    1. Fit an initial weak model (tree).
    2. Compute the residuals from the model.
    3. Fit a new tree to the residuals.
    4. Add the new tree to the ensemble, adjusting the weights of predictions.
    5. Repeat the process for a specified number of iterations or until the model performance improves sufficiently.

### Learning Rate
- **Definition**: The learning rate is a hyperparameter that controls how much each new tree contributes to the final prediction.
- **Role in Gradient Boosting**: A lower learning rate results in a more stable model with slower convergence, while a higher learning rate may lead to overfitting.

### Loss Function
- **Definition**: The loss function is used to evaluate how well the model is performing during training.
- **Common Loss Functions**:
  - **Mean Squared Error (MSE)**: Used for regression tasks to minimize the squared difference between predicted and true values.
  - **Log-Loss**: Used for classification tasks to minimize the error between predicted probabilities and true class labels.

---

## Interpretable Boosting

### Tree-based Feature Selection
- **Purpose**: One of the benefits of gradient boosting is its ability to perform implicit feature selection.
- **How It Works**: Features that are frequently used for splitting the data at each node in the decision trees are considered more important.

### Model Explainability
- **SHAP Values**: SHAP (Shapley Additive Explanations) is a method for interpreting the output of machine learning models, including Gradient Boosting. SHAP values help explain the contribution of each feature to the model’s predictions, providing insights into how the model works.
  
---

## Hyperparameters

### Key Hyperparameters:
- **n_estimators**: Number of trees in the model. More trees typically result in better accuracy, but may increase the risk of overfitting.
- **learning_rate**: Affects how quickly the model adapts to the data.
- **max_depth**: Maximum depth of the individual trees. Increasing this value allows the model to learn more complex patterns.
- **min_samples_split**: Minimum number of samples required to split an internal node. Increasing this value can prevent overfitting.
- **subsample**: Fraction of samples to use for fitting each tree. Using a lower fraction can prevent overfitting.

---

## Quantile Forecasting

- **Purpose**: Gradient Boosting can be adapted for quantile forecasting by predicting multiple quantiles of the target distribution, such as the 10th, 50th, and 90th percentiles, instead of a single point estimate.
- **Usage**: This allows users to obtain a range of possible future outcomes along with their uncertainty.

---

## Example Code Walkthrough

Here is an example of how to train a Gradient Boosting model using the `sklearn` library for a regression task:

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error

# Load dataset
data = pd.read_csv("data.csv")
X = data.drop("target", axis=1)  # Features
y = data["target"]  # Target variable

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize Gradient Boosting Regressor
model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)

# Train the model
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
