import pandas as pd
import os
import numpy as np
import re
from datetime import datetime

ticker = "INVH"

# List all regular CSV files in the directory
csv_files = [f for f in os.listdir() if f.startswith(ticker) and f.endswith('.csv')]
print(f"Found {len(csv_files)} regular CSV files for ticker {ticker}:")
for file in csv_files:
    print(f"  - {file}")

# Check if CPI.csv exists
cpi_file = "CPI.csv"
has_cpi = os.path.exists(cpi_file)
if has_cpi:
    print(f"Found CPI data file: {cpi_file}")
else:
    print(f"Warning: CPI data file {cpi_file} not found")

# Create a master date index dataframe first
master_dates = None

# First pass: collect all dates to create a complete date index
for file in csv_files:
    df = pd.read_csv(file)
    
    # Check if this file has date or date_idx column
    date_col = None
    if 'date' in df.columns:
        date_col = 'date'
        df['date'] = pd.to_datetime(df['date'])
    elif 'date_idx' in df.columns:
        date_col = 'date_idx'
    
    if date_col:
        # Extract just the date column to merge with master
        date_df = df[[date_col]].copy()
        
        # Initialize or merge with master dates
        if master_dates is None:
            master_dates = date_df
        else:
            master_dates = pd.merge(master_dates, date_df, on=date_col, how='outer')

if master_dates is None:
    print("No date or date_idx columns found in any files!")
    exit(1)

# Sort the master dates
date_col = master_dates.columns[0]
master_dates = master_dates.sort_values(date_col).reset_index(drop=True)
print(f"Created master date index with {len(master_dates)} unique dates")

# Second pass: Load each file and merge with master dates
merged_df = master_dates.copy()

for file in csv_files:
    # Extract the metric name from the filename
    metric = file.replace(f"{ticker}_", "").replace(".csv", "")
    
    # Read the CSV
    df = pd.read_csv(file)
    
    # Determine the date column and value column
    date_col = 'date_idx' if 'date_idx' in df.columns else 'date'
    
    # If the date column is 'date', convert to datetime
    if date_col == 'date':
        df['date'] = pd.to_datetime(df['date'])
    
    # Find the value column (typically not date/date_idx)
    value_cols = [col for col in df.columns if col != date_col]
    
    if not value_cols:
        print(f"Warning: No value columns found in {file}")
        continue
    
    # Merge with master dates dataframe
    temp_df = pd.merge(master_dates, df, on=date_col, how='left')
    
    # Apply linear interpolation to fill missing values
    for col in value_cols:
        # First interpolate linearly
        temp_df[col] = temp_df[col].interpolate(method='linear')
        
        # Add the interpolated column to the merged dataframe
        merged_df[col] = temp_df[col]
    
    print(f"Merged and interpolated {metric} data from {file}")

# Process CPI data if available
if has_cpi:
    # Read CPI data
    cpi_df = pd.read_csv(cpi_file)
    print(f"CPI data shape: {cpi_df.shape}")
    print(f"CPI columns: {', '.join(cpi_df.columns)}")
    
    # Convert CPI period notation (e.g., 2014 M01) to proper date
    def convert_period_to_date(year, period):
        month = int(period[1:]) if period.startswith('M') else 1
        return pd.Timestamp(year=int(year), month=month, day=1)
    
    # Create a datetime column from Year and Period
    cpi_df['date'] = cpi_df.apply(lambda row: convert_period_to_date(row['Year'], row['Period']), axis=1)
    
    # Keep only the date and value columns
    cpi_df = cpi_df[['date', 'Value']].rename(columns={'Value': 'cpi'})
    
    # Sort CPI data by date
    cpi_df = cpi_df.sort_values('date').reset_index(drop=True)
    
    # If the master dataframe uses date_idx instead of date, convert CPI dates
    if date_col == 'date_idx':
        # We need to calculate date_idx for CPI based on the reference date
        # Let's check the first rows of the merged dataframe to determine the reference date
        if 'date' in merged_df.columns:
            # We already have both date and date_idx
            ref_date = merged_df.loc[0, 'date']
            ref_idx = merged_df.loc[0, 'date_idx']
            cpi_df['date_idx'] = (cpi_df['date'] - ref_date).dt.days + ref_idx
        else:
            # We need to establish a reference date
            # For simplicity, let's assume date_idx 1 corresponds to 2009-03-31
            ref_date = pd.Timestamp('2009-03-31')
            cpi_df['date_idx'] = (cpi_df['date'] - ref_date).dt.days + 1
        
        # Merge based on date_idx
        merged_df = pd.merge(merged_df, cpi_df[['date_idx', 'cpi']], on='date_idx', how='left')
    else:
        # Merge based on date
        merged_df = pd.merge(merged_df, cpi_df[['date', 'cpi']], on='date', how='left')
    
    # Interpolate missing CPI values
    merged_df['cpi'] = merged_df['cpi'].interpolate(method='linear')
    
    print(f"Merged and interpolated CPI data")

# Display information about the merged dataframe
print("\nMerged dataframe info:")
print(f"Shape: {merged_df.shape}")
print(f"Columns: {', '.join(merged_df.columns)}")

# Drop any duplicate columns that might have been created during merging
merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

# Format all numeric columns to 3 decimal places
for col in merged_df.columns:
    if col != date_col and pd.api.types.is_numeric_dtype(merged_df[col]):
        merged_df[col] = merged_df[col].round(3)

# Save the merged dataframe
output_file = f"{ticker}_merged.csv"
merged_df.to_csv(output_file, index=False, float_format='%.3f')
print(f"\nSaved merged data to {output_file} with all values formatted to 3 decimal places")

# Show first 5 rows of the merged dataframe
print("\nFirst 5 rows of merged dataframe:")
print(merged_df.head())