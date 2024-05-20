import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

# Title of the app
st.title("3D Scatter Plot with Plotly and Streamlit")

# Predefined file path
file_path = "data/injury data/ITA Data CY 2016_cleaned.csv"

# Load the CSV file into a DataFrame
df = pd.read_csv(file_path)

df['injury_rate'] = df['total_injuries'] / df['annual_average_employees']

# Display the DataFrame
st.write("DataFrame:")
st.write(df)

col1, col2, col3, col4 = st.columns(4)
# Placeholder for 3D scatter plot fields
with col1:
    x_field = st.selectbox("Select X-axis field", df.columns)
with col2:
    y_field = st.selectbox("Select Y-axis field", df.columns)
with col3:
    z_field = st.selectbox("Select Z-axis field", df.columns)
with col4:
    color_field = st.selectbox("Select Color field", df.columns)

# Create 3D scatter plot
fig = px.scatter_3d(df, x=x_field, y=y_field, z=z_field, color=color_field, height=800, log_x=True, log_y=True, log_z=True)

# Display the 3D scatter plot
st.plotly_chart(fig,use_container_width=True)
