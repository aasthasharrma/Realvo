# Temporal Fusion Transformer (TFT) Documentation

The Temporal Fusion Transformer (TFT) is a deep learning model designed for multi-horizon time series forecasting. It combines recurrent neural networks (RNNs), attention mechanisms, gating networks, and variable selection to make forecasts. One thing that stands out about TFTs is that they can provide insights into the factors driving those forecasts. (TODO: learn more about how those insights work)

---

## Data Types

### Static Covariates 
- **Definition:** Features that remain constant over time (e.g., region).
- **Role in TFT:** These are processed through a static covariate encoder to produce dense embeddings and context vectors. These context vectors then influence other parts of the model by informing which features or time steps should be emphasized.

### Time-Varying Known Reals (`time_varying_known_reals`)
- **Definition:** Features that change over time but are known in advance (e.g., holidays, scheduled events).
- **Role in TFT:** These provide future context to the model, helping it adjust forecasts for planned events or calendar effects.

### Time-Varying Unknown Reals (`time_varying_unknown_reals`)
- **Definition:** Features that change over time but are not available for future time steps (e.g., historical market data, sensor readings).
- **Role in TFT:** They include the target variable and other dynamic inputs.

---

## Model Structure

### Static Covariate Encoder
- **Purpose:** Converts static features into embeddings and generates context vectors.
- **Why Encoders Are Needed:**  
  - **Transforming Data:** Encoders transform sparse or categorical inputs into a continuous, dense representation that the model can process more effectively.
  - **Providing Context:** The resulting context vectors (such as `cs` for temporal variable selection) are injected into later stages of the model, guiding feature selection and temporal processing.

### Variable Selection Networks
- **Purpose:** Dynamically weigh input features at each time step to select the most relevant ones.
- **Usage:**  
  - **Filtering Noise:** By assigning higher weights to important features and lower weights to less relevant ones, these networks help focus the model’s learning capacity on the most impactful data.
  - **Application Across Inputs:** Separate variable selection networks are applied to static, known, and unknown inputs.

### LSTM-based Local Processing (Encoder-Decoder)
- **What Are LSTMs?**
  - **Definition:** Long Short-Term Memory (LSTM) networks are a type of recurrent neural network (RNN) that efficiently capture sequential dependencies by maintaining a cell state with gating mechanisms (input, forget, and output gates). These gates regulate the flow of information and help preserve long-term dependencies.
  - **How They Work:** LSTMs update their internal state at each time step based on both the current input and the previous state, making them ideal for time series data.
- **Role in TFT:**
  - **Local Feature Extraction:** An LSTM-based sequence-to-sequence (seq2seq) layer processes a fixed-length historical window to extract local temporal patterns.
  - **Encoder-Decoder Framework:**  
    - **Encoder:** Summarizes past observations into a hidden representation.
    - **Decoder:** Uses this summary—augmented by static context—to generate forecasts for multiple future time steps.
- **Integration with the Model:**  
  The local processing layer provides rich, short-term temporal features that are then enhanced by static covariate information and later refined by the attention mechanism for long-term dependencies.

### Interpretable Multi-Head Attention - How the fuck does this even work at all? Someone please explain.
- **Purpose:** Captures long-term dependencies by allowing the model to focus on different time steps in the input sequence.
- **How It Works:**
  - **Multi-Head Structure:** Splits the attention mechanism into multiple “heads” so that each head can learn to focus on different aspects or patterns within the data.
  - **Interpretability:** The attention weights can be inspected to understand which past time steps have the most influence on the forecast, providing insight into the model’s decision process.

### Quantile Forecasting
- **Purpose:** Provides prediction intervals by forecasting multiple quantiles (e.g., 10th, 50th, 90th percentiles) rather than just a point estimate.
- **Usage:**  
  - **Uncertainty Estimation:** This method allows users to assess the range of possible future outcomes. 

---

## How the Components Link Together

1. **Static Covariate Processing:**  
   - Static features are first passed through the static covariate encoder, transforming them into embeddings and context vectors. These vectors guide variable selection and influence the processing of temporal features.

2. **Dynamic Variable Selection:**  
   - For both known and unknown time-varying inputs, variable selection networks compute weights to determine the relevance of each feature at every time step, effectively filtering out noise and emphasizing key inputs.

3. **LSTM-based Local Processing:**  
   - An encoder-decoder structure (using LSTMs) processes historical data to capture short-term patterns. The encoder compresses past information, and the decoder uses this compressed representation (enhanced with static context) to generate predictions for future time steps.

4. **Attention for Long-Term Dependencies:**  - Apperently this will help with prediciton transparency.?
   - The interpretable multi-head attention layer takes the output from the local processing stage and learns which time steps (or temporal patterns) are important for making long-term predictions. 

5. **Quantile Output Generation:**  
   - The final layer transforms the processed features into forecasts for various quantiles, offering a comprehensive view of possible future outcomes along with their uncertainty.

---

# Classes and Methods Explanation

This section provides detailed explanations of the main classes and methods used in the TFT code example.

---

## `TimeSeriesDataSet` (from `pytorch_forecasting.data`)

- **Purpose:**  
  Wraps and preprocesses raw time series data for forecasting tasks.

- **Key Parameters:**
  - `data`: A pandas DataFrame containing the time series data.
  - `time_idx`: Name of the column representing the time index.
  - `target`: The column name of the target variable to forecast.
  - `group_ids`: A list of column names that uniquely identify each time series.
  - `min_encoder_length` / `max_encoder_length`: Define the lookback window (i.e., the number of historical time steps to use).
  - `min_prediction_length` / `max_prediction_length`: Define the forecast horizon (i.e., the number of future time steps to predict).
  - `time_varying_known_reals`: List of continuous features known in advance (e.g., time indices, holidays).
  - `time_varying_unknown_reals`: List of continuous features only known historically (e.g., the target variable).
  - `target_normalizer`: Normalizes the target variable (e.g., using `GroupNormalizer`).
  - `add_relative_time_idx`: Automatically adds a column with a relative time index for normalization and learning.
  - `add_encoder_length`: Adds a column to indicate the encoder length for each time series.
  - `allow_missing_timesteps`: Allows the dataset to handle missing time steps gracefully.

- **Method:**
  - `to_dataloader(train, batch_size, num_workers)`:  
    Converts the `TimeSeriesDataSet` into a PyTorch DataLoader. This method batches the data and enables efficient data loading during model training.

---

## `TemporalFusionTransformer` (from `pytorch_forecasting`)

- **Purpose:**  
  Implements the Temporal Fusion Transformer (TFT) model architecture, which is designed for multi-horizon time series forecasting.

- **Class Method:**
  - `from_dataset(dataset, **kwargs)`  
    **Description:**  
    Creates a TFT model by inferring necessary parameters from the provided `TimeSeriesDataSet`.  
    **Key Hyperparameters:**
    - `learning_rate`: The step size for optimization.
    - `hidden_size`: Dimensionality of hidden states used in LSTMs and GRNs.
    - `attention_head_size`: Number of attention heads in the multi-head attention mechanism.
    - `dropout`: Dropout rate for regularization.
    - `hidden_continuous_size`: Dimensionality used for continuous variable embeddings.
    - `output_size`: Dimension of the model’s output (typically 1 for univariate forecasting).
    - `loss`: Loss function used during training (e.g., SMAPE).
    - `log_interval`: Frequency (in iterations) for logging training progress.

---

## `SMAPE` (from `pytorch_forecasting.metrics`)

- **Purpose:**  
  Computes the Symmetric Mean Absolute Percentage Error (SMAPE), which is used as the loss function to evaluate the accuracy of the forecasts.

- **Role in Training:**  
  SMAPE quantifies prediction error during training, guiding the optimization process toward better forecasting performance.

---

## `Trainer` (from `lightning.pytorch`)

- **Purpose:**  
  Manages the training process for the model, including the training loop, validation, logging, and checkpointing.

- **Key Parameters:**
  - `max_epochs`: Specifies the maximum number of epochs (complete passes through the training dataset) for which the model will be trained.

- **Method:**
  - `fit(model, train_dataloaders, val_dataloaders)`  
    **Description:**  
    Trains the provided model using the given training and validation DataLoaders. This method handles the entire training loop and monitors validation performance for early stopping or learning rate adjustments.


## Example Code Walkthrough

Below is an example of how to set up, train, and use the TFT model using PyTorch Forecasting:

```python
import pandas as pd
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from lightning.pytorch import Trainer
from pytorch_forecasting.metrics import SMAPE
from pytorch_forecasting.data import GroupNormalizer

# Load data
df = pd.read_csv("mock_data.csv")

# Define forecast horizon and encoder length
max_prediction_length = 14  # Number of future time steps to predict
max_encoder_length = 5      # Number of historical time steps to use

# Determine the training cutoff
training_cutoff = df["time_idx"].max() - max_prediction_length

# Create a TimeSeriesDataSet
training = TimeSeriesDataSet(
    df[lambda x: x.time_idx <= training_cutoff],  # Use data up to the cutoff
    time_idx="time_idx",                          # Time index column
    target="target",                              # Target variable for forecasting
    group_ids=["stallion"],                       # Series identifier column
    min_encoder_length=max_encoder_length,
    max_encoder_length=max_encoder_length,
    min_prediction_length=max_prediction_length,
    max_prediction_length=max_prediction_length,
    time_varying_known_reals=["time_idx"],         # Known continuous features
    time_varying_unknown_reals=["target"],         # Unknown continuous features (e.g., target)
    target_normalizer=GroupNormalizer(groups=["stallion"], transformation="softplus"),
    add_relative_time_idx=True,  # Adds a relative time index for normalization
    add_encoder_length=True,     # Adds encoder length information
    allow_missing_timesteps=True # Allows missing timesteps in the data
)

# Create DataLoaders for training and validation
batch_size = 64
train_dataloader = training.to_dataloader(train=True, batch_size=batch_size, num_workers=11)
val_dataloader = training.to_dataloader(train=False, batch_size=batch_size, num_workers=11)

# Initialize the Temporal Fusion Transformer model from the dataset
tft = TemporalFusionTransformer.from_dataset(
    training,
    learning_rate=0.03,
    hidden_size=16,             # Hidden layer size (affects LSTM and GRNs)
    attention_head_size=1,      # Number of attention heads (affects interpretability)
    dropout=0.1,                # Dropout rate for regularization
    hidden_continuous_size=8,   # Size for processing continuous variables
    output_size=1,              # Output dimension. hardcoded to 1. KNOWN_BUG: breaks if > 1
    loss=SMAPE(),               # Loss function used (SMAPE in this case)
    log_interval=10,            # Logging frequency - how often to log metrics
)

# Train the model using PyTorch Lightning's Trainer
trainer = Trainer(max_epochs=20)
trainer.fit(
    tft,
    train_dataloaders=train_dataloader,
    val_dataloaders=val_dataloader,
)
