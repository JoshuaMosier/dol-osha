import json
import numpy as np

# Path to the filtered JSON file
input_file = 'filtered_aggregated_data.json'
output_file = 'reformatted_aggregated_data.json'

# Load the filtered data
with open(input_file, 'r') as json_file:
    filtered_data = json.load(json_file)

# Initialize a dictionary to store the reformatted data
reformatted_data = {}

# Define the range of years to check
years = range(2016, 2024)

# Extract keys from one of the years (assuming all years have the same keys)
sample_year = next(iter(filtered_data.values()))
sample_keys = next(iter(sample_year.values())).keys()

# Reformat data
for establishment_id, yearly_data in filtered_data.items():
    reformatted_data[establishment_id] = {key: [None] * len(years) for key in sample_keys}
    
    for i, year in enumerate(years):
        year_str = str(year)
        if year_str in yearly_data:
            for key in sample_keys:
                reformatted_data[establishment_id][key][i] = yearly_data[year_str].get(key, None)
        else:
            for key in sample_keys:
                reformatted_data[establishment_id][key][i] = None

# Save the reformatted data to a new JSON file
with open(output_file, 'w') as json_file:
    json.dump(reformatted_data, json_file, indent=4)

print(f'Data successfully reformatted and saved to {output_file}')
