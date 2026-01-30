import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
import numpy as np

def create_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Shabhodaf20@mysql',
            database='clinical_trials'
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def clean_row_data(row):
    """Clean row data by replacing 'nan' strings with None"""
    cleaned_row = []
    for value in row:
        if pd.isna(value) or str(value).lower() == 'nan':
            cleaned_row.append(None)
        else:
            cleaned_row.append(value)
    return tuple(cleaned_row)

def import_mysql_ready_files():
    """Import MySQL-ready CSV files to MySQL database"""
    
    # Check if MySQL-ready files exist with your specific names
    files_to_check = ['trials_mysql_ready.csv', 'locations_mysql_ready.csv', 
                     'conditions_mysql_ready.csv', 'interventions_mysql_ready.csv']
    
    for file in files_to_check:
        if not os.path.exists(file):
            print(f"❌ Missing MySQL-ready file: {file}")
            return False
        else:
            print(f"✅ Found: {file}")
    
    connection = create_db_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    
    try:
        print("\n📥 Importing trials data...")
        trials_df = pd.read_csv('trials_mysql_ready.csv')
        
        # Handle date conversion for MySQL
        trials_df['start_date'] = pd.to_datetime(trials_df['start_date'], errors='coerce').dt.date
        trials_df['completion_date'] = pd.to_datetime(trials_df['completion_date'], errors='coerce').dt.date
        
        trials_count = 0
        for _, row in trials_df.iterrows():
            cleaned_row = clean_row_data(row)
            cursor.execute("""
                INSERT INTO trials (nct_id, title, status, phase, study_type, sponsor, 
                                  start_date, completion_date, enrollment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, cleaned_row)
            trials_count += 1
        
        print(f"✅ Imported {trials_count} trials")
        
        print("\n📥 Importing locations data...")
        locations_df = pd.read_csv('locations_mysql_ready.csv')
        locations_count = 0
        for _, row in locations_df.iterrows():
            cleaned_row = clean_row_data(row)
            cursor.execute("""
                INSERT INTO locations (nct_id, country, state, city, facility)
                VALUES (%s, %s, %s, %s, %s)
            """, cleaned_row)
            locations_count += 1
        print(f"✅ Imported {locations_count} locations")
        
        print("\n📥 Importing conditions data...")
        conditions_df = pd.read_csv('conditions_mysql_ready.csv')
        conditions_count = 0
        for _, row in conditions_df.iterrows():
            cleaned_row = clean_row_data(row)
            cursor.execute("""
                INSERT INTO conditions (nct_id, condition_name)
                VALUES (%s, %s)
            """, cleaned_row)
            conditions_count += 1
        print(f"✅ Imported {conditions_count} conditions")
        
        print("\n📥 Importing interventions data...")
        interventions_df = pd.read_csv('interventions_mysql_ready.csv')
        interventions_count = 0
        for _, row in interventions_df.iterrows():
            cleaned_row = clean_row_data(row)
            cursor.execute("""
                INSERT INTO interventions (nct_id, intervention_type, intervention_name)
                VALUES (%s, %s, %s)
            """, cleaned_row)
            interventions_count += 1
        print(f"✅ Imported {interventions_count} interventions")
        
        connection.commit()
        print("\n🎉 All data imported successfully!")
        
        # Print summary
        print(f"\n📊 IMPORT SUMMARY:")
        print(f"Trials: {trials_count:,}")
        print(f"Locations: {locations_count:,}")
        print(f"Conditions: {conditions_count:,}")
        print(f"Interventions: {interventions_count:,}")
        
        return True
        
    except Error as e:
        print(f"❌ Error importing data: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

# Run the import
if __name__ == "__main__":
    print("🚀 Starting MySQL Import with MySQL-Ready Files...")
    success = import_mysql_ready_files()
    if success:
        print("\n✅ Ready for Power BI! You can now connect to your MySQL database.")
    else:
        print("\n❌ Import failed. Please check the error messages above.")