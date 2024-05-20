import base64
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import json
import streamlit.components.v1 as components

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

    # Filter for non-zero injuries
    data = data.loc[data['total_injuries'] != 0]
    
    # Drop rows with NaN values in key columns
    data_cleaned = data.dropna(subset=['annual_average_employees', 'injury_rate'])
    
    return data_cleaned

@st.cache_data
def load_business_data():
    with open('data/sample_by_estab_id.json') as f:
        data = json.load(f)
    return data

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Home","Correlation Analysis", "NAICS Treemap", "Business Injury Rates","State Injury Rate Trends","3D Scatterplots","DAFW by VA ZIP"])

if page == "Home":
    st.title("OSHA Data Visualization Webapp")
    st.write("""
    This webapp provides various visualizations and analyses of OSHA data related to workplace injuries. Use the sidebar to navigate through the different pages, each offering unique insights into the data.
    
    - **Correlation Analysis**: Explore relationships between various injury-related metrics.
    - **NAICS Treemap**: View businesses grouped by NAICS code, colored by injury rates.
    - **Business Injury Rates**: Examine detailed injury data for specific businesses.
    - **State Injury Rate Trends**: Analyze injury rate trends across different states over time.
    - **3D Scatterplots**: Visualize multidimensional data with interactive scatter plots.
    - **DAFW by VA ZIP**: See the distribution of days away from work grouped by ZIP codes in Virginia.

    Select a page from the sidebar to begin exploring the data!
    """)
    
    st.subheader("About the Data")
    st.write("""
    The data used in this webapp is sourced from the Occupational Safety and Health Administration (OSHA) Injury Tracking Application (ITA). 
    The ITA collects data from establishments about work-related injuries and illnesses as required by OSHA's recordkeeping regulations. 
    The data includes details such as the number of injuries, illnesses, and fatalities, as well as the total hours worked and the number of employees.
    
    The first year of data collection was for calendar year (CY) 2016, with subsequent years collected annually. 
    Establishments with 250 or more employees and those with 20-249 employees in certain high-risk industries must submit their OSHA Form 300A data electronically each year.
    """)
    
    st.subheader("Data Dictionary")

    # Display PDF
    dict_url = 'https://www.osha.gov/sites/default/files/summary_data_dictionary.pdf'
    st.markdown("The following document provides a detailed explanation of the variables included in the dataset: [Data Dictionary](%s)" % dict_url)

# Correlation Analysis page
elif page == "Correlation Analysis":
    
    # Set up the main page and navigation
    st.title("Injury Rate Analysis Dashboard")
    
    year_select,name_search = st.columns(2)
    
    placeholder = 'Select a year'
    with year_select:
        year = st.selectbox("Select year for data",list(reversed(range(2016,2024))),index = 7)
    
    if year != placeholder:
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
            x_log = st.checkbox("Log scale for x-axis",value=True)
        with col2:
            y_field = st.selectbox("Select the field for the y-axis", numeric_fields, index=numeric_fields.index('total_dafw_days'))
            y_log = st.checkbox("Log scale for y-axis",value=True)
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
                value=(0.15, filter_max),
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
        
        # Display DataFrame
        if st.checkbox('Show raw data'):
            st.write(data_filtered)
    
elif page == "NAICS Treemap":
    st.title('OSHA Injury Data Treemap')
    col1,col2 = st.columns(2)
    with col1:
        st.subheader('Businesses grouped by NAICS code \nColored by Injury Rate (total_injuries/total_employees)')
    with col2:
        year = st.selectbox("Select year for data", reversed(range(2016,2024)), index=0)
        df = load_data(year)

    filtered_df = df.groupby(['naics_code', 'industry_description']).agg(
        total_employees=('annual_average_employees', 'sum'),
        total_hours_worked=('total_hours_worked', 'sum'),
        total_injuries=('total_injuries', 'sum')
    ).reset_index()

    filtered_df['injury_rate'] = filtered_df['total_injuries'] / filtered_df['total_employees']
    filtered_df = filtered_df[filtered_df['total_employees'] > 50000]

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
    )

    # Update font size and format for treemap text
    fig.update_traces(texttemplate='%{label}', textfont_size=14)

    fig.update_layout(height=800)  # Adjust height here

    st.plotly_chart(fig, use_container_width=True)

elif page == "Business Injury Rates":
    
    def style_row(row, skip_keys):
        # Check if the row should be skipped
        if row.name in skip_keys:
            return ['' for _ in row]

        numeric_cols = row.apply(lambda x: isinstance(x, (int, float)) and pd.notna(x))
        numeric_values = row[numeric_cols]

        if numeric_values.nunique() == 1:  # Check if all numeric values are identical
            return ['' for _ in row]

        min_val = numeric_values.min()
        max_val = numeric_values.max()
        range_val = max_val - min_val if max_val != min_val else 1

        styled_row = row.copy()
        for col in row.index:
            if numeric_cols[col]:
                value = row[col]
                intensity = (value - min_val) / range_val
                red_intensity = int(255 * intensity)
                color = f'rgb({red_intensity}, 0, 0)'  # Gradient from black to red
                styled_row[col] = f'background-color: {color}; color: white'  # White text for readability
            else:
                styled_row[col] = ''
        return styled_row

    # Streamlit app layout
    st.title('Business Data Visualization')

    data = load_business_data()
    # Extract business IDs and corresponding first non-null company names and establishment names
    business_info = {
        biz_id: (
            next((name for name in biz_data['company_name'] if name), 'N/A'),
            next((name for name in biz_data['establishment_name'] if name), 'N/A'),
            sum(x for x in biz_data['annual_average_employees'] if x is not None) / len([x for x in biz_data['annual_average_employees'] if x is not None]),
            sum(x for x in biz_data['total_injuries'] if x is not None) / len([x for x in biz_data['total_injuries'] if x is not None]),
        )
        for biz_id, biz_data in data.items()
    }
    business_info_df = pd.DataFrame(
        [(biz_id, info[0], info[1], info[2], info[3], info[3]/info[2]) for biz_id, info in business_info.items()],
        columns=['Business ID', 'Company Name', 'Establishment Name','Avg Annual Employees','Avg Annual Injuries','Avg Annual Injuries/Employee']
    )

    # Search bar to filter based on establishment name
    search_term = st.text_input('Search Establishment Name').lower()
    filtered_business_info_df = business_info_df[
        business_info_df['Establishment Name'].str.lower().str.contains(search_term)
    ]

    # Display filtered business IDs and company names table
    st.dataframe(filtered_business_info_df,use_container_width=True,hide_index=True)

    # Search box to enter business ID
    business_id = st.text_input('Enter Business ID')

    if business_id in data:
        business_data = data[business_id]
        
        # Display business information in a table
        years = list(range(2016, 2024))
        business_df = pd.DataFrame(business_data, index=years).T
        st.write("### Business Information")

        # Define the list of row keys to skip for stylization
        skip_keys = ['id', 'zip_code', 'year_filing_for']  # Replace with your actual keys

        # Apply row-wise color scale styling, skipping specified rows
        styled_df = business_df.style.apply(lambda row: style_row(row, skip_keys), axis=1)

        # Display the styled dataframe
        st.dataframe(styled_df, use_container_width=True,height=1000)
        
        # Prepare data for the calculated values
        fields_to_calculate = [
            'total_injuries', 'total_poisonings', 'total_respiratory_conditions',
            'total_skin_disorders', 'total_hearing_loss', 'total_other_illnesses'
        ]
        
        if all(field in business_data for field in fields_to_calculate) and 'annual_average_employees' in business_data:
            df_calculations = pd.DataFrame({'Year': years})
            for field in fields_to_calculate:
                df_calculations[field] = [
                    v / h if v is not None and h is not None and h != 0 else None 
                    for v, h in zip(business_data[field], business_data['annual_average_employees'])
                ]

            # Plot the calculated values
            fig = go.Figure()
            for field in fields_to_calculate:
                fig.add_trace(go.Scatter(x=df_calculations['Year'], y=df_calculations[field], mode='lines', name=field))

            fig.update_layout(title='Injury Types/Total Employees', xaxis_title='Year', yaxis_title='Value')
            st.plotly_chart(fig, use_container_width=True)
            
        # Prepare data for plotting
        year_data = {'Year': years}
        for key, values in business_data.items():
            if all(isinstance(v, (int, float)) for v in values):
                year_data[key] = values

        # Convert to DataFrame
        all_df = pd.DataFrame(year_data)

        # Plot all numeric key data
        fig = px.line(all_df, x='Year', y=all_df.columns[1:], title='Business Data Over Years')

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write('Business ID not found.')

elif page == "State Injury Rate Trends":
    # Function to load the preprocessed state_year_metrics data
    @st.cache_data
    def load_state_data():
        return pd.read_csv('data/state_year_metrics.csv')

    # Load the preprocessed data
    state_year_metrics = load_state_data()

    # Calculate global min and max for the color scale
    global_min = state_year_metrics['avg_injuries_per_employee'].min()
    global_max = state_year_metrics['avg_injuries_per_employee'].max()

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
        range_color=(global_min, global_max), # Set consistent color scale
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
    st.title("Injury Rate (injuries/employees) by State (2016-2023)")

    # Display dataframe
    st.dataframe(state_year_metrics, hide_index=True, use_container_width=True)
    
    st.plotly_chart(fig_choropleth, use_container_width=True)

    st.write("### State-wise Metrics Over Time")
    st.write("""
    This table shows the average injuries per employee for each state over the years with a color scale.
    """)

    # Display the styled pivot table
    st.dataframe(styled_table.format("{:.4f}"),use_container_width=True)

    st.plotly_chart(fig_line, use_container_width=True)

elif page == "3D Scatterplots":
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

    col1, col2, col3, col4, col5 = st.columns(5)
    # Placeholder for 3D scatter plot fields
    with col1:
        x_field = st.selectbox("Select X-axis field", df.columns, index=11)
    with col2:
        y_field = st.selectbox("Select Y-axis field", df.columns, index=17)
    with col3:
        z_field = st.selectbox("Select Z-axis field", df.columns, index=19)
    with col4:
        color_field = st.selectbox("Select Color field", df.columns, index=len(df.columns)-1)
    with col5:
        injury_rate_range = st.slider("Injury Rate Range", 0.0, 1.0, (0.3, 1.0))

    # Filter the DataFrame based on the selected injury rate range
    df_filtered = df[(df['injury_rate'] >= injury_rate_range[0]) & (df['injury_rate'] <= injury_rate_range[1])]

    # Create 3D scatter plot
    fig = px.scatter_3d(df_filtered, x=x_field, y=y_field, z=z_field, color=color_field, height=800, log_x=True, log_y=True, log_z=True, color_continuous_scale='temps')

    # Update trace to set marker size
    fig.update_traces(marker=dict(size=3, sizeref=1))
    
    # Display the 3D scatter plot
    st.plotly_chart(fig, use_container_width=True)
    
elif page == 'DAFW by VA ZIP':
    st.title("Days away from work grouped by VA Zip Code")
    
    with open('html/ita-data-map-va.html','r') as f: 
        html_data = f.read()
    
    st.components.v1.html(html_data, scrolling=True, height=600)