import pandas as pd
from functools import reduce

ticker = "SPG"

# Load the DataFrames with parsed 'date' column
df1 = pd.read_csv(f"{ticker}_assets.csv", parse_dates=['date'])
df2 = pd.read_csv(f"{ticker}_cap_rate.csv", parse_dates=['date'])
df3 = pd.read_csv(f"{ticker}_cash_on_hand.csv", parse_dates=['date'])
df4 = pd.read_csv(f"{ticker}_debt_to_equity.csv", parse_dates=['date'])
df5 = pd.read_csv(f"{ticker}_ebitda.csv", parse_dates=['date'])
df6 = pd.read_csv(f"{ticker}_eps.csv", parse_dates=['date'])
df7 = pd.read_csv(f"{ticker}_gross_profit.csv", parse_dates=['date'])
df8 = pd.read_csv(f"{ticker}_long_term_debt.csv", parse_dates=['date'])
df9 = pd.read_csv(f"{ticker}_market_cap.csv", parse_dates=['date'])
df10 = pd.read_csv(f"{ticker}_net_income.csv", parse_dates=['date'])
df11 = pd.read_csv(f"{ticker}_NOI.csv", parse_dates=['date'])
df12 = pd.read_csv(f"{ticker}_revenue.csv", parse_dates=['date'])
df13 = pd.read_csv(f"{ticker}_total_liabilities.csv", parse_dates=['date'])
df14 = pd.read_csv(f"{ticker}_total_shareholder_equity.csv", parse_dates=['date'])

# List of all dataframes
dfs = [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14]

# Merge all dataframes on 'date'
merged_df = reduce(lambda left, right: pd.merge(left, right, on='date', how='outer'), dfs)

# Optional: sort by date
merged_df = merged_df.sort_values('date').reset_index(drop=True)

# Output the merged dataframe
print(merged_df.head())

# Optional: Save the merged dataframe to a CSV
merged_df.to_csv(f"{ticker}_merged.csv", index=False)


print("Merged DataFrame created successfully with all date_idx values included!")

# Convert 'date' column to datetime
merged_df['date'] = pd.to_datetime(merged_df['date'])

# Define the start date
start_date = pd.Timestamp("2009-03-31")

# Compute the index as days since start_date + 1
merged_df['date_idx'] = (merged_df['date'] - start_date).dt.days + 1

# Drop the old 'date' column
merged_df.drop(columns=['date'], inplace=True)

# Save the modified CSV
merged_df.to_csv("SPG_merged.csv", index=False)

print("CSV file updated with date_idx!")
