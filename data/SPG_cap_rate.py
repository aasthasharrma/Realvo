#THIS ASSUMES THAT SPG_NOI.csv and SPG_assets.csv have already been created in the same directory as this script

import pandas as pd

# load data
noi_df = pd.read_csv("SPG_NOI.csv")
assets_df = pd.read_csv("SPG_assets.csv")

# merge the dataframes on the date column
merged_df = pd.merge(noi_df, assets_df, on="date")

# calculate cap rate
merged_df["cap_rate"] = merged_df["NOI"] / merged_df["assets"]

# save to new CSV, merge date and cap rate
merged_df[["date", "cap_rate"]].to_csv("SPG_cap_rate.csv", index=False)

print("SPG_cap_rate.csv has been created successfully.")
