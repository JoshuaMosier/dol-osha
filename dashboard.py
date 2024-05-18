import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide")

# Load the data
@st.cache_data
def load_data(year):
    file_path = 'data/injury data/ITA Data CY '+ str(year) +'_cleaned.csv'
    data = pd.read_csv(file_path)
    
    # Data cleaning and extraction
    data['total_hours_worked'] = pd.to_numeric(data['total_hours_worked'], errors='coerce')
    data['total_injuries'] = pd.to_numeric(data['total_injuries'], errors='coerce')
    data['annual_average_employees'] = pd.to_numeric(data['annual_average_employees'], errors='coerce')

    # Calculate the injury rate per employee
    data['injury_rate'] = data['total_injuries'] / data['annual_average_employees']

    # Drop rows with NaN values in key columns
    data_cleaned = data.dropna(subset=['annual_average_employees', 'injury_rate'])
    
    return data_cleaned

# Set up the main page and navigation
st.title("Injury Rate Analysis Dashboard")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Correlation Analysis", "Other Analysis"])

# Correlation Analysis page
if page == "Correlation Analysis":
    # Display the raw data
    st.write("### Dataframe")
    
    year_select,name_search = st.columns(2)
    
    with year_select:
        year = st.selectbox("Select year for data", reversed(range(2016,2024)), index=0)
        data_cleaned = load_data(year)
    with name_search:
        search_column = 'establishment_name'  # Update with the name of the column you want to search
        search_term = st.text_input(f'Search in {search_column}')
    
    # Filter data based on search term
    if search_term:
        filtered_df = data_cleaned[data_cleaned[search_column].str.contains(search_term, case=False, na=False)]
        # Display filtered data
        st.dataframe(filtered_df)
    else:
        st.dataframe(data_cleaned)
        
    # Dropdowns for selecting x and y axis fields
    numeric_fields = data_cleaned.select_dtypes(include=['number']).columns.tolist()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        x_field = st.selectbox("Select the field for the x-axis", numeric_fields, index=numeric_fields.index('total_hours_worked'))
        x_log = st.checkbox("Log scale for x-axis")
    with col2:
        y_field = st.selectbox("Select the field for the y-axis", numeric_fields, index=numeric_fields.index('total_dafw_days'))
        y_log = st.checkbox("Log scale for y-axis")
    with col3:
        color_field = st.selectbox("Select the field for color scale", numeric_fields, index=numeric_fields.index('injury_rate'))
        color_log = st.checkbox("Log scale for color field")
    with col4:
        filter_min, filter_max = 0.0, 1.0  # Default values
        if color_field:
            if color_log:
                valid_color_data = data_cleaned[color_field].replace([np.inf, -np.inf], np.nan).dropna()
                filter_min, filter_max = float(valid_color_data.min()), float(valid_color_data.max())
            else:
                filter_min, filter_max = float(data_cleaned[color_field].min()), float(data_cleaned[color_field].max())
        selected_range = st.slider(
            "Select range for color scale",
            min_value=filter_min,
            max_value=filter_max,
            value=(filter_min, filter_max),
        )

    # Define hover data
    hover_data = {
        'company_name': True,
        'id': True,
        'naics_code': True,
        'state': True,
        'city': True,
        'industry_description': True,
        'annual_average_employees': True,
        'total_injuries': True,
        'injury_rate': True
    }

    # Transform the color field to log scale if needed
    if color_field:
        if color_log:
            data_cleaned['log_color'] = np.log1p(data_cleaned[color_field])  # log1p to handle zero values
            color_col = 'log_color'
            color_label = color_field + " (log scale)"
        else:
            color_col = color_field
            color_label = color_field

        data_filtered = data_cleaned[(data_cleaned[color_field] >= selected_range[0]) & (data_cleaned[color_field] <= selected_range[1])]

        fig = px.scatter(
            data_filtered, 
            x=x_field, 
            y=y_field, 
            title=f"Scatter Plot of {x_field} vs {y_field}",
            log_x=x_log,
            log_y=y_log,
            color=color_col,  # Use the transformed or original color field
            color_continuous_scale=px.colors.sequential.Sunset,
            hover_data=hover_data
        )

        # Update color bar title to reflect the scale
        fig.update_coloraxes(colorbar_title=color_label)
    else:
        fig = px.scatter(
            data_cleaned, 
            x=x_field, 
            y=y_field, 
            title=f"Scatter Plot of {x_field} vs {y_field}",
            log_x=x_log,
            log_y=y_log,
            hover_data=hover_data
        )

    # Customize hover template
    fig.update_traces(
        hovertemplate="<br>".join([
            "Company: %{customdata[0]}",
            "Company ID: %{customdata[1]}",
            "NAICS Code: %{customdata[2]}",
            "State: %{customdata[3]}",
            "City: %{customdata[4]}",
            "Industry: %{customdata[5]}",
            "Employees: %{customdata[6]}",
            "Total Injuries: %{customdata[7]}",
            "Injury Rate: %{customdata[8]:.2f}"
        ])
    )
    
    fig.update_layout(height=800)  # Adjust height here
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display the correlation coefficient
    correlation = data_cleaned[x_field].corr(data_cleaned[y_field])
    st.write(f"Correlation coefficient between {x_field} and {y_field}: {correlation}")

elif page == "Other Analysis":
    st.header("Other Analysis")
    st.write("This section will contain additional analyses in the future.")
