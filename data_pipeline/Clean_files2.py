# clean_csv_for_mysql.py
import pandas as pd
import numpy as np

def clean_csv_for_mysql():
    """Clean CSV files specifically for MySQL import"""
    
    files = {
        'trials_cleaned.csv': 'trials_mysql_ready.csv',
        'locations_cleaned.csv': 'locations_mysql_ready.csv',
        'conditions_cleaned.csv': 'conditions_mysql_ready.csv', 
        'interventions_cleaned.csv': 'interventions_mysql_ready.csv'
    }
    
    for input_file, output_file in files.items():
        print(f"Cleaning {input_file}...")
        df = pd.read_csv(input_file)
        
        # Replace all NaN and string 'nan' with empty strings or appropriate values
        df = df.replace(['nan', 'NaN', ''], None)
        df = df.replace({np.nan: None})
        
        # Save cleaned version
        df.to_csv(output_file, index=False)
        print(f"✅ Saved: {output_file}")
    
    print("\n🎉 All files cleaned for MySQL import!")

clean_csv_for_mysql()