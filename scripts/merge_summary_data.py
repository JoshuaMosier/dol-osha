import pandas as pd
import os

# Directory where the CSV files are stored
directory = 'data/'

# Initialize an empty DataFrame to hold the combined data
combined_df = pd.DataFrame()

# List of years to process
years = range(2016, 2024)

for year in years:
    file_name = f'ITA Data CY {year}.csv'
    file_path = os.path.join(directory, file_name)
    
    if os.path.exists(file_path):
        try:
            # Try reading the CSV file with default 'utf-8' encoding
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            # If there's an encoding error, try reading with 'latin1' encoding
            df = pd.read_csv(file_path, encoding='latin1')
        
        # Add a column to track the original file name
        df['source_file'] = file_name
        
        # Drop duplicate rows within the file
        df.drop_duplicates(inplace=True)
        
        # Append to the combined DataFrame
        combined_df = pd.concat([combined_df, df], ignore_index=True)

# Drop duplicates across the combined DataFrame
combined_df.drop_duplicates(inplace=True)

# Sort by year to keep the most recent entries in case of duplicates
combined_df.sort_values(by='source_file', ascending=False, inplace=True)

# Drop duplicates again, keeping the first occurrence (most recent year due to sorting)
combined_df.drop_duplicates(subset=combined_df.columns.difference(['source_file']), keep='first', inplace=True)

# Save the combined DataFrame to a new CSV file
output_file = os.path.join(directory, 'ita-data-all.csv')
combined_df.to_csv(output_file, index=False)

print(f"Combined data saved to {output_file}")
