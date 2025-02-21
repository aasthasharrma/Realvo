import pandas as pd
import calendar

# Load the data
df = pd.read_csv("../data/CPI.csv")

# Convert 'Period' column (M01, M02, etc.) into month numbers
df['Month'] = df['Period'].str.extract(r'M(\d+)').astype(int)

# Create an empty list to store expanded rows
expanded_rows = []

# Loop through each row and expand dates
for _, row in df.iterrows():
    year = row['Year']
    month = row['Month']
    days_in_month = calendar.monthrange(year, month)[1]  # Get number of days in the month
    
    # Generate a row for each day in the month
    for day in range(1, days_in_month + 1):
        new_row = row.copy()
        new_row['date_idx'] = f"{year}-{month:02d}-{day:02d}"  # Format YYYY-MM-DD
        expanded_rows.append(new_row)

# Convert the list into a DataFrame
expanded_df = pd.DataFrame(expanded_rows)

# Drop unnecessary columns (e.g., 'Period', 'Month', 'Label', etc.)
expanded_df = expanded_df.drop(columns=['Period', 'Month', 'Label', 'Series ID', 'Year'])  # Adjust columns to drop as needed

# Rename 'Value' column to 'CPI'
expanded_df = expanded_df.rename(columns={'Value': 'CPI'})

# Convert 'date_idx' to datetime format
expanded_df['date_idx'] = pd.to_datetime(expanded_df['date_idx'])

# Define the reference start date
start_date = pd.Timestamp("2014-01-01")

# Compute the new index: days since Jan 1, 2014 (Jan 1, 2014 = 1, Jan 2, 2014 = 2, etc.)
expanded_df['date_idx'] = (expanded_df['date_idx'] - start_date).dt.days + 1

# Save the expanded data to a new CSV file
expanded_df.to_csv("CPI_cleaned.csv", index=False)

print("CSV file expanded: Dates indexed sequentially from Jan 1, 2014!")