import pandas as pd

def clean_osha_data(file_path):
    # Attempt to load the data with different encodings if utf-8 fails
    encodings = ['utf-8', 'ISO-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Failed to read the file with available encodings")

    # Remove duplicate rows
    df = df.drop_duplicates()
    
    # Handle missing values (dropping rows with any missing values for simplicity)
    df = df.dropna(subset=[
        'establishment_name', 'street_address', 'city', 'state', 'zip_code', 'naics_code', 
        'annual_average_employees', 'total_hours_worked', 'total_deaths', 'total_dafw_cases', 
        'total_djtr_cases', 'total_other_cases', 'total_dafw_days', 'total_djtr_days', 'total_injuries', 
        'total_skin_disorders', 'total_respiratory_conditions', 'total_poisonings', 'total_hearing_loss', 
        'total_other_illnesses', 'establishment_id', 'size', 'year_filing_for', 'created_timestamp'
    ])
    
    # Correct data formatting
    df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)
    df['naics_code'] = df['naics_code'].astype(str).str.zfill(6)
    
    # Ensure numeric columns are of numeric type
    numeric_columns = [
        'annual_average_employees', 'total_hours_worked', 'total_deaths', 
        'total_dafw_cases', 'total_djtr_cases', 'total_other_cases', 
        'total_dafw_days', 'total_djtr_days', 'total_injuries', 
        'total_skin_disorders', 'total_respiratory_conditions', 
        'total_poisonings', 'total_hearing_loss', 'total_other_illnesses'
    ]
    
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove rows with more injuries than annual average employees
    df = df[df['total_injuries'] <= df['annual_average_employees']]
    
    # Remove rows where total hours worked are less than a quarter of expected or more than double
    expected_hours_worked = df['annual_average_employees'] * 40 * 52
    df = df[(df['total_hours_worked'] >= 0.25 * expected_hours_worked) & (df['total_hours_worked'] <= 2 * expected_hours_worked)]
    
    # Ensure logical consistency in injury data
    df = df[(df['total_injuries'] >= df['total_skin_disorders'] + df['total_respiratory_conditions'] + 
             df['total_poisonings'] + df['total_hearing_loss'] + df['total_other_illnesses'])]
    
    # Remove rows with non-positive total hours worked
    df = df[df['total_hours_worked'] > 0]
    
    # Save the cleaned dataframe to a new CSV file
    cleaned_data_path = file_path.replace('.csv', '_cleaned.csv')
    df.to_csv(cleaned_data_path, index=False)
    return cleaned_data_path

# Example usage for multiple years of data
years = range(2016, 2024)
for year in years:
    file_path = f'data/injury data/ITA Data CY {year}.csv'
    try:
        cleaned_file_path = clean_osha_data(file_path)
        print(f'Cleaned data saved to: {cleaned_file_path}')
    except Exception as e:
        print(f'Failed to clean data for year {year}: {e}')
