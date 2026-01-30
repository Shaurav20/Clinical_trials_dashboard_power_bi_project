import pandas as pd
import numpy as np
from datetime import datetime
import re

def clean_trials_data():
    """Clean and structure trials data"""
    df = pd.read_csv('trials.csv')
    
    print("Trials data shape:", df.shape)
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nData types:")
    print(df.dtypes)
    
    # Data cleaning
    df_clean = df.copy()
    
    # Clean NCT ID (primary key)
    df_clean['nct_id'] = df_clean['nct_id'].astype(str).str.strip().str.upper()
    
    # Clean text fields - only apply string operations to string columns
    text_columns = ['title', 'status', 'phase', 'study_type', 'sponsor']
    for col in text_columns:
        if col in df_clean.columns:
            # Convert to string first, then clean
            df_clean[col] = df_clean[col].astype(str).str.strip()
            if col != 'phase':  # Don't apply title case to phase yet
                df_clean[col] = df_clean[col].str.title()
    
    # Handle missing values
    print("\nBefore cleaning - Missing values:")
    print(df_clean.isnull().sum())
    
    # Standardize phase values
    phase_mapping = {
        'phase 1': 'Phase 1',
        'phase 2': 'Phase 2', 
        'phase 3': 'Phase 3',
        'phase 4': 'Phase 4',
        'early phase 1': 'Phase 1',
        'not applicable': 'N/A',
        'nan': 'N/A',
        '': 'N/A'
    }
    df_clean['phase'] = df_clean['phase'].str.lower().replace(phase_mapping).fillna('N/A')
    
    # Clean enrollment - convert to numeric
    df_clean['enrollment'] = pd.to_numeric(df_clean['enrollment'], errors='coerce')
    
    # Standardize status values
    status_mapping = {
        'completed': 'Completed',
        'recruiting': 'Recruiting',
        'active, not recruiting': 'Active',
        'not yet recruiting': 'Not Recruiting',
        'terminated': 'Terminated',
        'suspended': 'Suspended',
        'withdrawn': 'Withdrawn',
        'unknown status': 'Unknown',
        'enrolling by invitation': 'Recruiting',
        'active': 'Active'
    }
    df_clean['status'] = df_clean['status'].str.lower().replace(status_mapping)
    
    # Date cleaning - handle different date formats
    date_columns = ['start_date', 'completion_date']
    for col in date_columns:
        # First convert to string, then to datetime
        df_clean[col] = df_clean[col].astype(str)
        # Replace empty strings with NaT
        df_clean[col] = df_clean[col].replace('nan', pd.NaT)
        df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce', format='mixed')
    
    # Handle sponsor column (completely missing)
    df_clean['sponsor'] = df_clean['sponsor'].replace('nan', 'Unknown')
    
    # Remove duplicates
    df_clean = df_clean.drop_duplicates(subset=['nct_id'])
    
    print(f"\nAfter cleaning - Missing values:")
    print(df_clean.isnull().sum())
    print(f"\nCleaned trials data: {df_clean.shape}")
    
    return df_clean

def clean_locations_data():
    """Clean and structure locations data"""
    df = pd.read_csv('locations.csv')
    
    print("Locations data shape:", df.shape)
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nData types:")
    print(df.dtypes)
    
    df_clean = df.copy()
    
    # Clean NCT ID
    df_clean['nct_id'] = df_clean['nct_id'].astype(str).str.strip().str.upper()
    
    # Clean location fields - convert to string first
    location_columns = ['country', 'state', 'city', 'facility']
    for col in location_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
    
    # Standardize country names
    country_mapping = {
        'United States': 'USA',
        'United States Of America': 'USA',
        'Usa': 'USA',
        'United Kingdom': 'UK',
        'Uk': 'UK',
        'Nan': 'Unknown'
    }
    df_clean['country'] = df_clean['country'].replace(country_mapping)
    
    # Remove rows with no location information
    df_clean = df_clean[~(df_clean['country'].isin(['Unknown', 'Nan']) & 
                         df_clean['city'].isin(['Unknown', 'Nan']))]
    
    print(f"\nCleaned locations data: {df_clean.shape}")
    return df_clean

def clean_conditions_data():
    """Clean and structure conditions data"""
    df = pd.read_csv('conditions.csv')
    
    print("Conditions data shape:", df.shape)
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nData types:")
    print(df.dtypes)
    
    df_clean = df.copy()
    
    # Clean NCT ID
    df_clean['nct_id'] = df_clean['nct_id'].astype(str).str.strip().str.upper()
    
    # Clean condition names
    df_clean['condition'] = df_clean['condition'].astype(str).str.strip().str.title()
    
    # Remove empty conditions
    df_clean = df_clean[df_clean['condition'] != '']
    df_clean = df_clean[df_clean['condition'] != 'Nan']
    
    # Remove duplicates (same condition for same trial)
    df_clean = df_clean.drop_duplicates()
    
    print(f"\nCleaned conditions data: {df_clean.shape}")
    return df_clean

def clean_interventions_data():
    """Clean and structure interventions data"""
    df = pd.read_csv('interventions.csv')
    
    print("Interventions data shape:", df.shape)
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nData types:")
    print(df.dtypes)
    
    df_clean = df.copy()
    
    # Clean NCT ID
    df_clean['nct_id'] = df_clean['nct_id'].astype(str).str.strip().str.upper()
    
    # Clean intervention fields
    df_clean['intervention_type'] = df_clean['intervention_type'].astype(str).str.strip().str.title()
    df_clean['intervention_name'] = df_clean['intervention_name'].astype(str).str.strip().str.title()
    
    # Standardize intervention types
    type_mapping = {
        'Drug': 'Drug',
        'Biological': 'Biological',
        'Device': 'Device',
        'Procedure': 'Procedure',
        'Behavioral': 'Behavioral',
        'Genetic': 'Genetic',
        'Radiation': 'Radiation',
        'Other': 'Other',
        'Nan': 'Unknown'
    }
    df_clean['intervention_type'] = df_clean['intervention_type'].replace(type_mapping)
    
    # Remove empty interventions
    df_clean = df_clean[~(df_clean['intervention_name'].isin(['', 'Nan']))]
    
    # Remove duplicates
    df_clean = df_clean.drop_duplicates()
    
    print(f"\nCleaned interventions data: {df_clean.shape}")
    return df_clean

# Run cleaning functions
print("=== CLEANING TRIALS DATA ===")
trials_clean = clean_trials_data()

print("\n=== CLEANING LOCATIONS DATA ===")
locations_clean = clean_locations_data()

print("\n=== CLEANING CONDITIONS DATA ===")
conditions_clean = clean_conditions_data()

print("\n=== CLEANING INTERVENTIONS DATA ===")
interventions_clean = clean_interventions_data()

# Save cleaned data
trials_clean.to_csv('trials_cleaned.csv', index=False)
locations_clean.to_csv('locations_cleaned.csv', index=False)
conditions_clean.to_csv('conditions_cleaned.csv', index=False)
interventions_clean.to_csv('interventions_cleaned.csv', index=False)

print("\nCleaned files saved!")

# Create a summary report
print("\n=== DATA QUALITY SUMMARY ===")
print(f"Trials: {trials_clean.shape[0]} records")
print(f"Locations: {locations_clean.shape[0]} records") 
print(f"Conditions: {conditions_clean.shape[0]} records")
print(f"Interventions: {interventions_clean.shape[0]} records")

# Check for any remaining issues
print("\n=== REMAINING DATA ISSUES ===")
print("Trials - Missing sponsor:", trials_clean['sponsor'].isnull().sum())
print("Trials - Missing enrollment:", trials_clean['enrollment'].isnull().sum())
print("Trials - Missing phase:", (trials_clean['phase'] == 'N/A').sum())