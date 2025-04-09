import pandas as pd
from functools import reduce

ticker = "SPG"

# Load the existing merged CSV
df = pd.read_csv("SPG_merged.csv")

# Add REIT_Return column (as net_income / total_shareholder_equity)
df["REIT_Return"] = df["netincome"] / df["totalshareholderequity"]

df = df.drop(columns=["cpi"])

# Save the modified CSV
df.to_csv("SPG_merged.csv", index=False)

print("CSV file updated with dropped cpi!")
