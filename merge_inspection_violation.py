import pandas as pd
import glob
import os

def merge_csv_files(folder_path, file_pattern):
    """
    Merge multiple CSV files into a single DataFrame.
    
    Parameters:
    - folder_path: The path to the folder containing the CSV files.
    - file_pattern: The pattern to match the CSV files (e.g., "osha_violation*.csv").
    
    Returns:
    - A merged DataFrame containing all the data from the matched CSV files.
    """
    all_files = glob.glob(os.path.join(folder_path, file_pattern))
    df_list = []
    
    for file in all_files:
        df = pd.read_csv(file)
        df_list.append(df)
    
    merged_df = pd.concat(df_list, ignore_index=True)
    return merged_df

def basic_data_cleaning(df):
    """
    Perform basic data cleaning on the DataFrame.
    
    Parameters:
    - df: The DataFrame to clean.
    
    Returns:
    - The cleaned DataFrame.
    """
    # Drop duplicate rows
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    # Convert date columns to datetime
    date_columns = ['open_date', 'close_case_date', 'issuance_date', 'abate_date', 'contest_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
    
    return df

# Paths to the folders containing the CSV files
osha_violation_folder = 'data/violations'
osha_inspection_folder = 'data/inspections'

# Merge the CSV files
osha_violation_df = merge_csv_files(osha_violation_folder, 'osha_violation*.csv')
osha_inspection_df = merge_csv_files(osha_inspection_folder, 'osha_inspection*.csv')

# Perform basic data cleaning
osha_violation_df_clean = basic_data_cleaning(osha_violation_df)
osha_inspection_df_clean = basic_data_cleaning(osha_inspection_df)

# Save the cleaned data to new CSV files
osha_violation_df_clean.to_csv('merged_cleaned_osha_violation.csv', index=False)
osha_inspection_df_clean.to_csv('merged_cleaned_osha_inspection.csv', index=False)

print("Data merging and cleaning completed successfully.")
