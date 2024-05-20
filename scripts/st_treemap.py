import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
@st.cache_data
def load_data(filepath):
    data = pd.read_csv(filepath)
    return data

st.set_page_config(layout='wide')
df = load_data('data/injury data/ITA Data CY 2016_cleaned.csv')

# Data Processing
df['injury_rate'] = df['total_injuries'] / df['total_hours_worked']
filtered_df = df.groupby(['naics_code', 'industry_description']).agg(
    total_employees=('annual_average_employees', 'sum'),
    total_hours_worked=('total_hours_worked', 'sum'),
    total_injuries=('total_injuries', 'sum')
).reset_index()

filtered_df['injury_rate'] = filtered_df['total_injuries'] / filtered_df['total_hours_worked']
filtered_df = filtered_df[filtered_df['total_employees'] > 10000]

# Function to wrap text at 20 characters
def wrap_text(text, width=20):
    return '<br>'.join([text[i:i+width] for i in range(0, len(text), width)])

# Cap the industry description and format labels with wrapping
filtered_df['wrapped_industry_description'] = filtered_df['industry_description'].apply(lambda x: wrap_text(x))
filtered_df['label'] = filtered_df['wrapped_industry_description'] + '<br>(' + filtered_df['naics_code'].astype(str) + ')'

# Plotting
fig = px.treemap(
    filtered_df,
    path=['label'],
    values='total_employees',
    color='injury_rate',
    color_continuous_scale='reds',
    title='Treemap of NAICS Codes by Total Employees and Injury Rate'
)

# Update font size and format for treemap text
fig.update_traces(texttemplate='%{label}', textfont_size=14)

fig.update_layout(height=800)  # Adjust height here

# Streamlit App Layout
st.title('OSHA Injury Data Treemap')
st.plotly_chart(fig, use_container_width=True)

st.write("""
This treemap visualizes the distribution of NAICS codes based on the total number of annual average employees. 
The size of each cell represents the total employees, and the color represents the injury rate calculated 
as total hours worked divided by total injuries.
""")

st.write("""
Filtered to only include NAICS codes with more than 50,000 total annual employees.
""")

# Display DataFrame
if st.checkbox('Show raw data'):
    st.write(filtered_df)
