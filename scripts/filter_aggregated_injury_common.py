import json
from tqdm import tqdm

# Path to the aggregated JSON file
input_file = 'aggregated_injury_data.json'
output_file = 'filtered_aggregated_data.json'

# Load the aggregated data
with open(input_file, 'r') as json_file:
    aggregated_data = json.load(json_file)

# Initialize a dictionary to store the filtered data
filtered_data = {}

# Define the range of years to check
years = range(2016, 2024)

# Filter out establishment IDs with less than 5 year values
for establishment_id, data in tqdm(aggregated_data.items()):
    year_count = sum(1 for year in years if str(year) in data)
    if year_count >= 6:
        filtered_data[establishment_id] = data

# Save the filtered data to a new JSON file
with open(output_file, 'w') as json_file:
    json.dump(filtered_data, json_file, indent=4)

print(f'Data successfully filtered and saved to {output_file}')
