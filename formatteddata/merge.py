import pandas as pd


# Load the DataFrames (assuming CSV files)
df1 = pd.read_csv("cap_rate_cleaned.csv")  # First DataFrame
df2 = pd.read_csv("CPI_cleaned.csv")  # Second DataFrame
df3 = pd.read_csv("debt_to_equity_ratio_cleaned.csv")  # Third DataFrame
df4 = pd.read_csv("SPG_market_cap_cleaned.csv")  # Fourth DataFrame

# Ensure date_idx is in the correct format
df1["date_idx"] = pd.to_numeric(df1["date_idx"], errors="coerce")
df2["date_idx"] = pd.to_numeric(df2["date_idx"], errors="coerce")
df3["date_idx"] = pd.to_numeric(df3["date_idx"], errors="coerce")
df4["date_idx"] = pd.to_numeric(df4["date_idx"], errors="coerce")

# Merge all 4 DataFrames on 'date_idx' using an outer join
merged_df = df1.merge(df2, on="date_idx", how="outer") \
               .merge(df3, on="date_idx", how="outer") \
               .merge(df4, on="date_idx", how="outer")

# Sort by date index to maintain chronological order
merged_df = merged_df.sort_values(by="date_idx").reset_index(drop=True)

# Save the merged DataFrame to a CSV file
merged_df.to_csv("merged_data.csv", index=False)

print("Merged DataFrame created successfully with all date_idx values included!")

