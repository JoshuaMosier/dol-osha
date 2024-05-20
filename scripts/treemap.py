import pandas as pd
import plotly.express as px
import numpy as np

# Load the data (replace 'osha_data.csv' with the path to your dataset)
df = pd.read_csv('data/injury data/ITA Data CY 2023.csv')

# Handle missing values
df['industry_description'] = df['industry_description'].fillna('Unknown Industry')
df['annual_average_employees'] = df['annual_average_employees'].replace(0, np.nan).fillna(1)

# Combine industry name and NAICS code into a single column for display
df['industry_naics'] = df['industry_description'] + ' - (' + df['naics_code'].astype(str) + ')'

# Aggregate data by industry_naics
grouped_df = df.groupby('industry_naics').agg({
    'annual_average_employees': 'sum',
    'total_injuries': 'sum',
    'total_hours_worked': 'sum'
}).reset_index()

# Filter industries with more than 4000 annual employees
filtered_df = grouped_df[grouped_df['annual_average_employees'] > 50000].copy()

# Calculate the ratio of total_injuries to total_hours_worked
filtered_df.loc[:, 'injury_rate'] = filtered_df['total_injuries'] / filtered_df['total_hours_worked']

# Use a higher base log scale for the color
filtered_df.loc[:, 'log_injury_rate'] = np.log(filtered_df['injury_rate'] + 1) / np.log(2)  # Using log base 2

# Create the treemap with a more distinct color scale
fig = px.treemap(
    filtered_df,
    path=['industry_naics'],
    values='annual_average_employees',
    color='log_injury_rate',
    color_continuous_scale='Viridis',  # Choose a distinct color scale
    title='Treemap of OSHA Injuries by Industry with Log-scaled Injury Rate Color'
)

fig.update_coloraxes(colorbar_title='Log Injury Rate (Base 2)')

fig.show()