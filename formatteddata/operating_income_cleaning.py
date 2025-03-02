import pandas as pd

# Load the quarterly data
df = pd.read_csv("SPG_Quarterly_Operating_Income.csv")

# Convert Date column to datetime format
df["Date"] = pd.to_datetime(df["Date"])

# Remove dollar signs and convert "Quarterly Operating Income" to float
df["Quarterly Operating Income"] = df["Quarterly Operating Income"].replace('[\$,]', '', regex=True).astype(float)

# Set Date as index
df.set_index("Date", inplace=True)

# Create a complete daily date range from the first to the last date
full_date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq="D")

# Reindex the DataFrame to include all dates
df_daily = df.reindex(full_date_range)

# Interpolate missing values at a constant rate (linear interpolation)
df_daily["Quarterly Operating Income"] = df_daily["Quarterly Operating Income"].interpolate(method="linear")

# Reset index and rename columns
df_daily.reset_index(inplace=True)
df_daily.rename(columns={"index": "Date", "Quarterly Operating Income": "Daily Estimated Operating Income"}, inplace=True)

# Generate a date index starting from Jan 1, 2014
start_date = "2014-01-01"
end_date = "2024-12-31"
date_range = pd.date_range(start=start_date, end=end_date, freq="D")

# Create a DataFrame with an increasing index for each day
df_index = pd.DataFrame({"Date": date_range})
df_index["Date_Index"] = range(1, len(df_index) + 1)

# Merge daily operating income with the date index
df_final = pd.merge(df_index, df_daily, on="Date", how="left")

df_final.drop(columns=["Date"], inplace=True)

# Save the final CSV file
df_final.to_csv("SPG_Daily_Operating_Income_Indexed.csv", index=False)

print("Daily operating income with date index has been successfully saved.")