import pandas as pd
import torch
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from lightning.pytorch import Trainer
from pytorch_forecasting.metrics import SMAPE
from pytorch_forecasting.data import GroupNormalizer

# Load data
print("Loading data...")
df = pd.read_csv("SPG_merged.csv")

df['date'] = pd.to_datetime(df['date'])
df['time_idx'] = range(len(df))
df['group_id'] = 0  # Single group since it's one time series
df['v1'] = df['v1'].fillna(method='ffill').fillna(method='bfill')

# Define consistent parameters for both training and prediction
max_prediction_length = 14
max_encoder_length = 30
training_cutoff = int(len(df) * 0.8)  # Use 80% of data for training

# Define the same features to be used in both scripts
time_varying_known_reals = [
    "time_idx", "totalshareholderequity", "debttoequityratio", "grossprofit", 
    "revenue", "totalliabilities", "eps", "cashonhand", "NOI", "assets", 
    "ebitda", "netincome", "cap_rate", "longtermdebt"
]
time_varying_unknown_reals = ["v1"]

print(f"Creating TimeSeriesDataSet with encoder length: {max_encoder_length}, prediction length: {max_prediction_length}")
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

batch_size = 64

# Create data loaders
print("Creating data loaders...")
train_dataloader = training.to_dataloader(train=True, batch_size=batch_size, num_workers=0)
val_dataloader = training.to_dataloader(train=False, batch_size=batch_size, num_workers=0)

# Create TFT model
print("Initializing TFT model...")
tft = TemporalFusionTransformer.from_dataset(
    training,
    learning_rate=0.03,
    hidden_size=32,             # Increased for better capacity
    attention_head_size=2,      # Increased for better attention
    dropout=0.1,
    hidden_continuous_size=16,  # Increased for better representation
    output_size=1,
    loss=SMAPE(),
)

# Train the model
print("Training the model...")
trainer = Trainer(
    max_epochs=5,  # Increased for better convergence
    accelerator="auto",  # Use GPU if available
)
trainer.fit(
    tft,
    train_dataloaders=train_dataloader,
    val_dataloaders=val_dataloader,
)

# Save model parameters
print("Saving model...")
torch.save(tft.state_dict(), "model.pth")

# Save model configuration to a text file for reference
with open("model_config.txt", "w") as f:
    f.write(f"max_prediction_length = {max_prediction_length}\n")
    f.write(f"max_encoder_length = {max_encoder_length}\n")
    f.write(f"training_cutoff = {training_cutoff}\n")
    f.write(f"time_varying_known_reals = {time_varying_known_reals}\n")
    f.write(f"time_varying_unknown_reals = {time_varying_unknown_reals}\n")

print("Training complete! Model saved as 'model.pth'")