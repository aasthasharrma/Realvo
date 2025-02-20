import pandas as pd
import torch as torch
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from lightning.pytorch import Trainer
from pytorch_forecasting.metrics import SMAPE
from pytorch_forecasting.data import GroupNormalizer

# Load data
df = pd.read_csv("mock_data.csv")

# number of time points to predict into the future
max_prediction_length = 14

# Sets the  number of historical time steps the model must see
max_encoder_length = 5

# use all data for training (we will just predict the last few values)
training_cutoff = df["time_idx"].max() - max_prediction_length

training = TimeSeriesDataSet(
    df[lambda x: x.time_idx <= training_cutoff], # only include data up to the training cutoff
    time_idx = "time_idx", # specifies the time index column - required even though its already in the dataframe
    target = "target", # specifies the target column - required even though its already in the dataframe
    group_ids = ["stallion"], # specifies the series id column - required even though its already in the dataframe
    min_encoder_length = max_encoder_length, 
    max_encoder_length= max_encoder_length, 
    min_prediction_length=max_prediction_length,
    max_prediction_length=max_prediction_length,
    time_varying_known_reals=["time_idx"], # ex:["time_idx", "feat_dynamic_dog", "feat_dynamic_cat", etc] - continuous features known in advance
    time_varying_unknown_reals=["target"], # ex:["target", "estimate", etc] - continuous features not known in advance
    target_normalizer=GroupNormalizer(groups=["stallion"], transformation="softplus"), # normalizes the target based on the group
    add_relative_time_idx=True, # the dataset will add additional columns that store scaling information for the target variable. This allows the model to learn in a normalized space and later convert predictions back to the original scale.
    add_encoder_length=True, # adds a column to the dataset that stores the encoder length for each time series
    allow_missing_timesteps=True # allows for missing timesteps in the data #TODO: how does this work?
)

# TODO: create hyperparameter gridsearch module with wandb (old makoto code)
batch_size = 64 # number of time series to include in each batch

# DataLoader
# training data
train_dataloader = training.to_dataloader(train=True, batch_size=batch_size, num_workers=0) # KNOWN BUG: >0 num_workers breaks training loop. Weird that I had it working at 11 preciously.
# validation data
val_dataloader = training.to_dataloader(train=False, batch_size=batch_size, num_workers=0)

# create TFT model
tft = TemporalFusionTransformer.from_dataset(
    training,                   # training dataset
    learning_rate=0.03,         
    hidden_size=16,             
    attention_head_size=1,      # TODO: understand what this does and why it shouldn't be maxed out
    dropout=0.1,                # TODO: add hyperparameter search
    hidden_continuous_size=8,   # For continuous variables. TODO: find out what this does
    output_size=1,              # TODO: add hyperparameter search
    loss=SMAPE(),               # Use SMAPE as the loss function. This is the default loss function for the TFT TODO: find out what how this works.
)

# Train the model
trainer = Trainer(
    max_epochs=20, # hard coded for now.
)
trainer.fit(
    tft,
    train_dataloaders=train_dataloader,
    val_dataloaders=val_dataloader,
)

torch.save(tft.state_dict(), "model.pth")

# Predict - TODO: transform tensor to df
predictions = tft.predict(val_dataloader, mode="prediction")
print(predictions)
