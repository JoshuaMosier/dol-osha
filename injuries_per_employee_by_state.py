import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

# Function to load the preprocessed state_year_metrics data
@st.cache_data
def load_preprocessed_data():
    return pd.read_csv('data/state_year_metrics.csv')

# Load the preprocessed data
state_year_metrics = load_preprocessed_data()

# Pivot table for state-wise metrics
pivot_table = state_year_metrics.pivot(index='state', columns='year', values='avg_injuries_per_employee').fillna(0)

# Plotly choropleth map animation
fig_choropleth = px.choropleth(
    state_year_metrics,
    locations='state',
    locationmode='USA-states',
    color='avg_injuries_per_employee',
    hover_name='state',
    animation_frame='year',
    scope='usa',
    title='Cumulative Average of Injuries per Employee by State Over Time',
    color_continuous_scale='viridis',
    height=800,
)

# Plotly line graph
fig_line = px.line(
    state_year_metrics,
    x='year',
    y='avg_injuries_per_employee',
    color='state',
    title='Average Injuries per Employee by State Over Time',
    height=800,
)

styled_table = pivot_table.style.background_gradient(cmap='viridis')

# Streamlit app layout
st.title("OSHA Injury Data Analysis")
st.write("""
This app computes the cumulative average of total injuries per annual average employee for each state and displays a choropleth map that animates over time.
""")

st.plotly_chart(fig_choropleth, use_container_width=True)

st.write("### State-wise Metrics Over Time")
st.write("""
This table shows the average injuries per employee for each state over the years with a color scale.
""")

# Display the styled pivot table
st.dataframe(styled_table.format("{:.4f}"),use_container_width=True)

st.plotly_chart(fig_line, use_container_width=True)