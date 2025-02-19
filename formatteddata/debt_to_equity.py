import pandas as pd
import calendar

# Load the data
df = pd.read_csv("../data/SPG_debt_to_equity.csv")

print(df['date'])

# Convert 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

# Sort the data by date in ascending order to ensure proper interpolation
df = df.sort_values(by='date')

# Create a complete daily date range from the earliest to the latest date
full_date_range = pd.DataFrame({'date': pd.date_range(start=df['date'].min(), 
                                                      end=df['date'].max(), 
                                                      freq='D')})

# Merge to include all daily dates while keeping existing quarterly values
df = pd.merge(full_date_range, df, on='date', how='left')

# Interpolate 'cap_rate' values linearly for the daily data
df['debttoequityratio'] = df['debttoequityratio'].interpolate(method='linear')

print("Daily cap rate data generated with a constant rate of change between quarters!")
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

# Define the reference start date
start_date = pd.Timestamp("2014-01-01")

# Compute the new index: days since Jan 1, 2014 (Jan 1, 2014 = 1, Jan 2, 2014 = 2, etc.)
df["date"] = (df["date"] - start_date).dt.days + 1

df = df[df["date"] >= 1]
print(df['debttoequityratio']) 
df.rename(columns={'debttoequityratio': 'debt_to_equity_ratio'}, inplace=True)
df.rename(columns={'date': 'date_idx'}, inplace=True)
df.to_csv("debt_to_equity_ratio_cleaned.csv", index=False)

