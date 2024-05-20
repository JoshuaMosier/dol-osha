import os
import pandas as pd
import json

# Directory containing the CSV files
directory_path = 'data/injury data/'

# Initialize a dictionary to store the aggregated data
aggregated_data = {}

# Define the range of years you are interested in
years = range(2016, 2024)

# Loop through each year in the specified range
for year in years:
    filename = f'ITA Data CY {year}_cleaned.csv'
    file_path = os.path.join(directory_path, filename)
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        
        # Loop through each row in the dataframe
        for _, row in df.iterrows():
            establishment_id = row['establishment_id']
            
            if establishment_id not in aggregated_data:
                aggregated_data[establishment_id] = {}
            
            # Add data for the year
            aggregated_data[establishment_id][year] = row.to_dict()
    else:
        print(f"File for year {year} not found.")

# Save the aggregated data to a JSON file
output_file = 'aggregated_injury_data.json'
with open(output_file, 'w') as json_file:
    json.dump(aggregated_data, json_file, indent=4)

print(f'Data successfully aggregated and saved to {output_file}')
