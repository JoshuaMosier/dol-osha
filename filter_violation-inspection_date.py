import pandas as pd
from tqdm import tqdm

def filter_inspections(inspections_df):
    """
    Filter inspections to only include those with a close_case_date of 2020 or later.
    
    Parameters:
    - inspections_df: DataFrame containing inspection data.
    
    Returns:
    - Filtered DataFrame with inspections from 2020 or later.
    """
    inspections_df['close_conf_date'] = pd.to_datetime(inspections_df['close_conf_date'], format='%Y-%m-%d', errors='coerce')
    filtered_inspections = inspections_df[inspections_df['close_conf_date'].dt.year >= 2020]
    return filtered_inspections

def filter_violations(violations_df, filtered_inspections):
    """
    Filter violations to only include those with activity_nr present in the filtered inspections.
    
    Parameters:
    - violations_df: DataFrame containing violation data.
    - filtered_inspections: DataFrame containing filtered inspection data.
    
    Returns:
    - Filtered DataFrame with violations associated with the filtered inspections.
    """
    filtered_activity_nrs = set(filtered_inspections['activity_nr'])
    
    # Initialize an empty list to store filtered violations
    filtered_violations_list = []
    
    # Use tqdm to add a progress bar
    for index, row in tqdm(violations_df.iterrows(), total=violations_df.shape[0], desc="Filtering Violations"):
        if row['activity_nr'] in filtered_activity_nrs:
            filtered_violations_list.append(row)
    
    # Convert the list back to a DataFrame
    filtered_violations = pd.DataFrame(filtered_violations_list)
    
    return filtered_violations

# Read the merged cleaned data
# osha_inspection_df = pd.read_csv('merged_cleaned_osha_inspection.csv')
osha_violation_df = pd.read_csv('merged_cleaned_osha_violation.csv')

# Filter inspections and violations
# filtered_inspections_df = filter_inspections(osha_inspection_df)
filtered_inspections_df = pd.read_csv('filtered_osha_inspection.csv')
filtered_violations_df = filter_violations(osha_violation_df, filtered_inspections_df)

# Save the filtered data to new CSV files
# filtered_inspections_df.to_csv('filtered_osha_inspection.csv', index=False)
filtered_violations_df.to_csv('filtered_osha_violation.csv', index=False)

print("Data filtering completed successfully.")
