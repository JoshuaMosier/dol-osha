import pandas as pd
import glob

# Function to load the OSHA data for all years
def load_all_data():
    all_files = glob.glob('data/injury data/ITA Data CY *_cleaned.csv')
    df_list = []
    for file in all_files:
        year = int(file.split('CY ')[1].split('_')[0])
        df = pd.read_csv(file)
        df['year'] = year
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)

# Load all data
data = load_all_data()

# Function to clean the data
def clean_data(data):
    # Convert state abbreviations to uppercase
    data['state'] = data['state'].str.upper()

    # List of valid US state abbreviations
    valid_states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 
        'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 
        'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]

    # Filter out invalid state abbreviations
    data = data[data['state'].isin(valid_states)]

    return data

# Clean the data
data = clean_data(data)

# Data processing
data['injuries_per_employee'] = data['total_injuries'] / data['annual_average_employees']

# Compute cumulative metrics for each state and year
state_year_metrics = data.groupby(['state', 'year']).agg(
    total_injuries=('total_injuries', 'sum'),
    total_annual_average_employees=('annual_average_employees', 'sum')
).reset_index()

state_year_metrics['avg_injuries_per_employee'] = state_year_metrics['total_injuries'] / state_year_metrics['total_annual_average_employees']

# Save the state_year_metrics data to a CSV file
state_year_metrics.to_csv('data/state_year_metrics.csv', index=False)
