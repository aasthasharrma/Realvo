import pandas as pd

# Load the data
df = pd.read_csv("../data/SPG_market_cap.csv")

#This is to verify that the csv file was extracted correctly
#print(df['date'])

# Convert 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

# Define the reference start date
start_date = pd.Timestamp("2014-01-01")

# Compute the new index: days since Jan 1, 2014 (Jan 1, 2014 = 1, Jan 2, 2014 = 2, etc.)
df["date"] = (df["date"] - start_date).dt.days + 1

df = df[df["date"] >= 1]

#Add a new row in the

new_row = pd.DataFrame({'date': [1], 'v1': [47.24]})

# Concatenate the new row at the top
df = pd.concat([new_row, df], ignore_index=True)

# Create a full range of dates
full_dates = pd.DataFrame({'date': range(df['date'].min(), df['date'].max() + 1)})

# Create a complete range of dates from min to max
full_dates = pd.DataFrame({'date': range(df['date'].min(), df['date'].max() + 1)})

# Merge to add missing dates
df = pd.merge(full_dates, df, on='date', how='left')

# Fill missing 'v1' values with the previous row’s value
df['v1'] = df['v1'].ffill()

#rename the columns
df.rename(columns={'date': 'date_idx'}, inplace=True)
df.rename(columns={'v1': 'market_cap'}, inplace=True)
# Save to a new CSV file

df.to_csv("SPG_market_cap_cleaned.csv", index=False)

# print("CSV file with date indices saved successfully!")
