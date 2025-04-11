import pandas as pd
import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import SMAPE

# Function to calculate SMAPE
def calculate_smape(actual, predicted):
    """Calculate SMAPE between actual and predicted values"""
    raw_smape = np.mean(2 * np.abs(predicted - actual) / (np.abs(predicted) + np.abs(actual)))
    smape_percentage = 100 * raw_smape
    return raw_smape, smape_percentage

# Load the data
print("Loading data...")
df = pd.read_csv("SPG_merged.csv")
df['date'] = pd.to_datetime(df['date'])
df['time_idx'] = range(len(df))
df['group_id'] = 0  # Single group since it's one time series
# Use newer pandas syntax to avoid the FutureWarning
df['v1'] = df['v1'].ffill().bfill()

# Define model parameters - should match what was used during training
max_prediction_length = 14
max_encoder_length = 30
training_cutoff = int(len(df) * 0.8)

# Define the time-varying known variables
time_varying_known_reals = [
    "time_idx", "totalshareholderequity", "debttoequityratio", "grossprofit", 
    "revenue", "totalliabilities", "eps", "cashonhand", "NOI", "assets", 
    "ebitda", "netincome", "cap_rate", "longtermdebt"
]
time_varying_unknown_reals = ["v1"]

# Create training dataset (needed to initialize the model)
print("Creating training dataset...")
training = TimeSeriesDataSet(
    df[lambda x: x.time_idx <= training_cutoff],
    time_idx="time_idx",
    target="v1",
    group_ids=["group_id"],
    min_encoder_length=max_encoder_length,
    max_encoder_length=max_encoder_length,
    min_prediction_length=max_prediction_length,
    max_prediction_length=max_prediction_length,
    time_varying_known_reals=time_varying_known_reals,
    time_varying_unknown_reals=time_varying_unknown_reals,
    target_normalizer=GroupNormalizer(groups=["group_id"], transformation="softplus"),
    add_relative_time_idx=True,
    add_encoder_length=True,
    allow_missing_timesteps=True
)

# Initialize the model structure
print("Initializing model...")
tft = TemporalFusionTransformer.from_dataset(
    training,
    learning_rate=0.03,
    hidden_size=32,  # Increased to match saved model parameters
    attention_head_size=2,  # Adjusted to match saved model
    dropout=0.1,
    hidden_continuous_size=16,  # Increased to match saved model parameters
    output_size=1,
    loss=SMAPE(),
)

# Load the saved model weights
print("Loading model weights...")
tft.load_state_dict(torch.load("model.pth"))
tft.eval()  # Set to evaluation mode

# Create a validation dataset using the TimeSeriesDataSet.from_dataset method
print("Creating validation dataset...")
validation = TimeSeriesDataSet.from_dataset(
    training, 
    df[lambda x: x.time_idx > training_cutoff],
    predict=True,
    stop_randomization=True
)
val_dataloader = validation.to_dataloader(train=False, batch_size=64, num_workers=0)

# Generate predictions
print("Generating predictions...")
with torch.no_grad():
    predictions = tft.predict(val_dataloader, return_x=True, return_index=True)
    # Move tensors to CPU
    predictions_tensor = predictions.output.cpu()
    inputs = predictions.x
    indices = predictions.index
    
# Extract the time indices from indices
print("Processing results...")
time_indices = []
all_predictions = []
all_actuals = []

for batch_id in range(len(predictions_tensor)):
    # Get prediction start time from the index
    encoder_lengths = indices["encoder_length"][batch_id].cpu().numpy()
    encoder_time_idx = indices["encoder_time_idx"][batch_id].cpu().numpy()
    
    # Calculate the start time index for predictions (last encoder time + 1)
    start_time_idx = encoder_time_idx[encoder_lengths - 1] + 1
    
    # Get predictions for this batch
    preds = predictions_tensor[batch_id].numpy()
    
    # Time indices for this prediction
    pred_time_indices = np.arange(start_time_idx, start_time_idx + len(preds))
    
    for i, pred_idx in enumerate(pred_time_indices):
        if pred_idx < len(df):
            # Find the corresponding actual value
            actual_rows = df[df['time_idx'] == pred_idx]
            if not actual_rows.empty:
                actual_value = actual_rows['v1'].values[0]
                
                # Add to collections
                all_predictions.append(preds[i])
                all_actuals.append(actual_value)
                time_indices.append(pred_idx)

# Create visualization
print("Creating visualization...")
if len(all_predictions) > 0 and len(all_actuals) > 0:
    # Convert to numpy arrays
    all_predictions_array = np.array(all_predictions)
    all_actuals_array = np.array(all_actuals)
    time_indices_array = np.array(time_indices)
    
    # Calculate metrics
    smape_value, smape_percentage = calculate_smape(all_actuals_array, all_predictions_array)
    r2_value = r2_score(all_actuals_array, all_predictions_array)
    
    print(f"SMAPE: {smape_value:.4f} ({smape_percentage:.2f}%)")
    print(f"R²: {r2_value:.4f}")
    
    # Create the figure
    plt.figure(figsize=(16, 10))
    
    # Plot the actual data for the entire dataset
    plt.plot(df['time_idx'], df['v1'], 'r-', linewidth=1.5, label='Actual', alpha=0.7)
    
    # Plot predictions as scatter points
    plt.scatter(time_indices_array, all_predictions_array, color='blue', s=20, alpha=0.7, label='Predictions')
    
    # Add metrics to the plot
    plt.text(0.02, 0.97, f'SMAPE: {smape_value:.4f} ({smape_percentage:.2f}%)', 
            fontsize=12, transform=plt.gca().transAxes,
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
    
    plt.text(0.02, 0.92, f'R²: {r2_value:.4f}', 
            fontsize=12, transform=plt.gca().transAxes,
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
    
    # Add vertical line for train/validation split
    plt.axvline(x=training_cutoff, color='green', linestyle='--', linewidth=2)
    plt.text(training_cutoff + 10, plt.ylim()[1] * 0.95, 'Validation →', 
            fontsize=12, color='green')
    
    # Add an inset plot showing the prediction accuracy
    ax_inset = plt.axes([0.65, 0.15, 0.25, 0.25])  # [left, bottom, width, height]
    ax_inset.scatter(all_actuals_array, all_predictions_array, alpha=0.5, s=15)
    
    # Add diagonal line for perfect predictions
    min_val = min(min(all_actuals_array), min(all_predictions_array))
    max_val = max(max(all_actuals_array), max(all_predictions_array))
    ax_inset.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.8)
    
    ax_inset.set_xlabel('Actual Values')
    ax_inset.set_ylabel('Predicted Values')
    ax_inset.set_title('Prediction Accuracy')
    ax_inset.grid(True, alpha=0.3)
    
    # Add titles and labels
    plt.title('Model Predictions vs Actual Values', fontsize=16)
    plt.xlabel('Time Index', fontsize=12)
    plt.ylabel('Value (v1)', fontsize=12)
    plt.legend(loc='upper right', frameon=True, fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Save the figure with high resolution
    plt.savefig('model_predictions_vs_actuals.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create validation-only plot
    plt.figure(figsize=(16, 8))
    
    # Filter for validation period
    val_df = df[df['time_idx'] > training_cutoff]
    
    # Plot actuals for validation period
    plt.plot(val_df['time_idx'], val_df['v1'], 'r-', linewidth=2, label='Actual', alpha=0.7)
    
    # Plot predictions for validation period
    plt.scatter(time_indices_array, all_predictions_array, color='blue', s=30, alpha=0.7, label='Predictions')
    
    # Add metrics to the plot
    plt.text(0.02, 0.97, f'SMAPE: {smape_value:.4f} ({smape_percentage:.2f}%)', 
            fontsize=12, transform=plt.gca().transAxes,
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
    
    plt.text(0.02, 0.92, f'R²: {r2_value:.4f}', 
            fontsize=12, transform=plt.gca().transAxes,
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))
    
    # Add titles and labels
    plt.title('Model Predictions vs Actual Values (Validation Period Only)', fontsize=16)
    plt.xlabel('Time Index', fontsize=12)
    plt.ylabel('Value (v1)', fontsize=12)
    plt.legend(loc='upper right', frameon=True, fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Save the figure
    plt.savefig('validation_predictions.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualizations complete! Saved as 'model_predictions_vs_actuals.png' and 'validation_predictions.png'")
else:
    print("No predictions or actuals collected. Check the data and model parameters.")