import pandas as pd
import numpy as np
import torch
import matplotlib.pyplot as plt
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import SMAPE

# Load the data
df = pd.read_csv("SPG_merged.csv")

df['date'] = pd.to_datetime(df['date'])
df['time_idx'] = range(len(df))
df['group_id'] = 0  # Single group since it's one time series
df['v1'] = df['v1'].fillna(method='ffill').fillna(method='bfill')

# Define the same parameters used in train.py
max_prediction_length = 14
max_encoder_length = 5
training_cutoff = int(len(df) * 0.8)

# Define the same time-varying known variables as in train.py
time_varying_known_reals = [
    "time_idx", "totalshareholderequity", "debttoequityratio", "grossprofit", 
    "revenue", "totalliabilities", "eps", "cashonhand", "NOI", "assets", 
    "ebitda", "netincome", "cap_rate", "longtermdebt"
]
time_varying_unknown_reals = ["v1"]

# Recreate the training dataset (needed to initialize the model)
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

# Initialize the model with the same parameters as in train.py
tft = TemporalFusionTransformer.from_dataset(
    training,
    learning_rate=0.03,
    hidden_size=16,
    attention_head_size=1,
    dropout=0.1,
    hidden_continuous_size=8,
    output_size=1,
    loss=SMAPE(),
)

# Load the saved state dictionary
tft.load_state_dict(torch.load("model.pth"))

# Set the model to evaluation mode
tft.eval()

print("Model loaded successfully!")

# Create validation dataset
validation = TimeSeriesDataSet.from_dataset(
    training, 
    df[lambda x: x.time_idx > training_cutoff], 
    predict=True,
    stop_randomization=True
)
val_dataloader = validation.to_dataloader(train=False, batch_size=64, num_workers=0)

# Make predictions on validation data
print("Making predictions on validation data...")
predictions = tft.predict(val_dataloader, mode="prediction")

# Convert predictions to numpy for easier handling
predictions_np = predictions.cpu().numpy()

# Create a DataFrame with predictions
prediction_df = pd.DataFrame(
    predictions_np,
    columns=[f"t+{i}" for i in range(1, predictions_np.shape[1] + 1)]
)

# Add useful columns for analysis
validation_data = df[lambda x: x.time_idx > training_cutoff]
valid_indices = validation_data.index[:len(prediction_df)]  # Ensure we don't go out of bounds
if len(valid_indices) > 0:  # Check if there are any valid indices
    prediction_df['start_date'] = validation_data.loc[valid_indices, 'date'].values
    prediction_df['time_idx'] = validation_data.loc[valid_indices, 'time_idx'].values

print(f"Prediction shape: {predictions_np.shape}")
print(f"First few predictions:\n{prediction_df.head()}")

# Plot predictions against actuals
def plot_predictions(num_samples=5):
    plt.figure(figsize=(15, 8))
    
    for i in range(min(num_samples, len(prediction_df))):
        # Get the start index for this prediction
        start_idx = prediction_df['time_idx'].iloc[i]
        forecast_indices = range(start_idx + 1, start_idx + max_prediction_length + 1)
        
        # Get actual values for this period if available
        actual_indices = [idx for idx in forecast_indices if idx < len(df)]
        actuals = df.loc[df['time_idx'].isin(actual_indices), 'v1'].values
        
        # Plot prediction with semi-transparency
        plt.plot(forecast_indices, prediction_df.iloc[i, :max_prediction_length], 
                'b-', alpha=0.3, label='Prediction' if i == 0 else '')
        
        # Plot actuals if available
        if len(actuals) > 0:
            plt.plot(actual_indices, actuals, 
                    'r-', alpha=0.5, label='Actual' if i == 0 else '')
    
    plt.title('TFT Predictions vs Actuals')
    plt.xlabel('Time Index')
    plt.ylabel('Value (v1)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('prediction_plot.png')
    plt.show()

print("Plotting predictions...")
plot_predictions()

# Make future predictions
def predict_future(forecast_length=30):
    print(f"Predicting {forecast_length} steps into the future...")
    
    # Create a dataset with the last max_encoder_length points
    last_data = df.iloc[-max_encoder_length:].copy()
    
    # Create future time indices
    last_time_idx = df['time_idx'].max()
    future_indices = pd.DataFrame({
        'time_idx': range(last_time_idx + 1, last_time_idx + 1 + forecast_length),
        'group_id': 0
    })
    
    # For known reals, use the last values (simple assumption)
    for col in time_varying_known_reals:
        if col == 'time_idx':
            future_indices[col] = future_indices['time_idx']
        else:
            # Use last value for simplicity (you might want more sophisticated forecasting)
            future_indices[col] = df[col].iloc[-1]
    
    # For unknown reals (v1), we're predicting these so use NaN
    for col in time_varying_unknown_reals:
        future_indices[col] = float('nan')
    
    # Add date column
    last_date = df['date'].iloc[-1]
    future_indices['date'] = pd.date_range(
        start=last_date + pd.Timedelta(days=1), 
        periods=forecast_length, 
        freq='D'  # Adjust frequency as needed
    )
    
    # Combine with last known data
    forecast_df = pd.concat([last_data, future_indices])
    
    # Create dataset
    future_dataset = TimeSeriesDataSet(
        forecast_df,
        time_idx="time_idx",
        target="v1",
        group_ids=["group_id"],
        min_encoder_length=max_encoder_length,
        max_encoder_length=max_encoder_length,
        min_prediction_length=forecast_length,
        max_prediction_length=forecast_length,
        time_varying_known_reals=time_varying_known_reals,
        time_varying_unknown_reals=time_varying_unknown_reals,
        target_normalizer=GroupNormalizer(groups=["group_id"], transformation="softplus"),
        add_relative_time_idx=True,
        add_encoder_length=True,
        allow_missing_timesteps=True
    )
    
    # Create dataloader
    future_dataloader = future_dataset.to_dataloader(train=False, batch_size=1)
    
    # Get predictions
    future_predictions = tft.predict(future_dataloader)
    future_predictions = future_predictions.cpu().numpy()[0]
    
    # Create result dataframe
    result = pd.DataFrame({
        'date': future_indices['date'],
        'time_idx': future_indices['time_idx'],
        'predicted_v1': future_predictions
    })
    
    return result

# Make future predictions
future_forecast = predict_future(30)
print(future_forecast.head())

# Plot future predictions
plt.figure(figsize=(12, 6))
# Plot historical data (last 60 days)
hist_data = df.iloc[-60:]
plt.plot(hist_data['time_idx'], hist_data['v1'], 'b-', label='Historical')

# Plot future predictions
plt.plot(future_forecast['time_idx'], future_forecast['predicted_v1'], 'r--', label='Forecast')
plt.axvline(x=df['time_idx'].max(), color='green', linestyle='--', label='Present')
plt.title('Future Predictions')
plt.xlabel('Time Index')
plt.ylabel('Value (v1)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('future_forecast.png')
plt.show()

# Save predictions to CSV files
prediction_df.to_csv('validation_predictions.csv', index=False)
future_forecast.to_csv('future_predictions.csv', index=False)
print("Predictions saved to CSV files: 'validation_predictions.csv' and 'future_predictions.csv'")