import requests
import json
import csv
from datetime import datetime
import time

# -------------------------------
# Helper functions
# -------------------------------

def clean_date(date_str):
    if not date_str:
        return ""
    try:
        return datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        try:
            return datetime.strptime(date_str, "%B %Y").strftime("%Y-%m")
        except:
            return date_str

def safe_get_first(lst, default=""):
    """Safely get first element from list or return default"""
    return lst[0] if lst and len(lst) > 0 else default

# -------------------------------
# CONFIG
# -------------------------------

BATCH_SIZE = 100
all_studies = []
MAX_RETRIES = 3

print("Starting download from ClinicalTrials.gov API...")

# -------------------------------
# API v2 DOWNLOAD LOOP
# -------------------------------

base_url = "https://clinicaltrials.gov/api/v2/studies"
next_page_token = None
total_studies_retrieved = 0

# Correct field names for API v2
fields = [
    "NCTId",
    "BriefTitle",
    "Condition",
    "InterventionName",
    "InterventionType", 
    "LocationFacility",
    "LocationCity",
    "LocationState",
    "LocationCountry",
    "Phase",
    "StudyType",
    "OverallStatus",
    "LeadSponsorName",
    "StartDate",
    "PrimaryCompletionDate",
    "EnrollmentCount"
]

while True:
    # Build the query parameters for API v2
    params = {
        'query.term': 'cancer immunotherapy',
        'fields': ','.join(fields),
        'pageSize': BATCH_SIZE
    }
    
    # Add page token if we have one (for pagination)
    if next_page_token:
        params['pageToken'] = next_page_token

    print(f"Fetching batch...{' (page: ' + next_page_token + ')' if next_page_token else ''}")

    retry_count = 0
    success = False
    batch_data = None
    
    while retry_count < MAX_RETRIES and not success:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                retry_count += 1
                time.sleep(2)
                continue
                
            # Try to parse JSON
            batch_data = response.json()
            success = True
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            retry_count += 1
            time.sleep(2)
            continue
        except json.JSONDecodeError as e:
            print(f"JSON decode failed: {e}")
            print(f"Response text: {response.text[:500] if 'response' in locals() else 'No response'}")
            retry_count += 1
            time.sleep(2)
            continue

    if not success:
        print(f"Failed to fetch batch after {MAX_RETRIES} retries. Stopping.")
        break

    # Extract studies from the response
    studies = batch_data.get("studies", [])
    
    if not studies:
        print("No more data available.")
        break

    all_studies.extend(studies)
    total_studies_retrieved += len(studies)
    print(f"Retrieved {len(studies)} studies in this batch (Total: {total_studies_retrieved})")

    # Check for next page token
    next_page_token = batch_data.get("nextPageToken")
    
    if not next_page_token:
        print("No more pages available.")
        break

    time.sleep(1)  # Be respectful to the API

print(f"Total studies downloaded: {len(all_studies)}")

# If we got studies, let's inspect one to understand the structure
if all_studies:
    print("\nInspecting first study structure...")
    first_study = all_studies[0]
    print(json.dumps(first_study, indent=2)[:2000])  # First 2000 chars

# Only proceed if we have data
if not all_studies:
    print("No data to process. Exiting.")
    exit()

# -------------------------------
# CSV WRITERS
# -------------------------------

try:
    trials_file = open("trials.csv", "w", newline="", encoding="utf-8")
    trials_writer = csv.writer(trials_file)
    trials_writer.writerow([
        "nct_id", "title", "status", "phase",
        "study_type", "sponsor", "start_date",
        "completion_date", "enrollment"
    ])

    locations_file = open("locations.csv", "w", newline="", encoding="utf-8")
    locations_writer = csv.writer(locations_file)
    locations_writer.writerow(["nct_id", "country", "state", "city", "facility"])

    conditions_file = open("conditions.csv", "w", newline="", encoding="utf-8")
    conditions_writer = csv.writer(conditions_file)
    conditions_writer.writerow(["nct_id", "condition"])

    interventions_file = open("interventions.csv", "w", newline="", encoding="utf-8")
    interventions_writer = csv.writer(interventions_file)
    interventions_writer.writerow(["nct_id", "intervention_type", "intervention_name"])

    # -------------------------------
    # EXTRACT FIELDS INTO CSV
    # -------------------------------

    studies_processed = 0
    for study in all_studies:
        try:
            # Extract basic information using the flattened structure
            nct_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "")
            if not nct_id:
                continue

            # Get all the modules
            ident_module = study.get("protocolSection", {}).get("identificationModule", {})
            status_module = study.get("protocolSection", {}).get("statusModule", {})
            design_module = study.get("protocolSection", {}).get("designModule", {})
            sponsors_module = study.get("protocolSection", {}).get("sponsorsCollaboratorsModule", {})
            conditions_module = study.get("protocolSection", {}).get("conditionsModule", {})
            arms_interventions_module = study.get("protocolSection", {}).get("armsInterventionsModule", {})
            contacts_locations_module = study.get("protocolSection", {}).get("contactsLocationsModule", {})

            # TRIALS - Main table
            trials_writer.writerow([
                nct_id,
                ident_module.get("briefTitle", ""),
                status_module.get("overallStatus", ""),
                safe_get_first(design_module.get("phases", [])),
                design_module.get("studyType", ""),
                sponsors_module.get("leadSponsor", {}).get("name", "") if sponsors_module.get("leadSponsor") else "",
                clean_date(status_module.get("startDateStruct", {}).get("date", "")),
                clean_date(status_module.get("primaryCompletionDateStruct", {}).get("date", "")),
                status_module.get("enrollment", {}).get("count", "") if isinstance(status_module.get("enrollment"), dict) else status_module.get("enrollment", "")
            ])

            # LOCATIONS
            locations = contacts_locations_module.get("locations", [])
            for location in locations:
                locations_writer.writerow([
                    nct_id,
                    location.get("country", ""),
                    location.get("state", ""),
                    location.get("city", ""),
                    location.get("facility", "")
                ])

            # CONDITIONS
            conditions = conditions_module.get("conditions", [])
            for condition in conditions:
                conditions_writer.writerow([nct_id, condition])

            # INTERVENTIONS
            interventions = arms_interventions_module.get("interventions", [])
            for intervention in interventions:
                interventions_writer.writerow([
                    nct_id,
                    intervention.get("type", ""),
                    intervention.get("name", "")
                ])
                
            studies_processed += 1
            
        except Exception as e:
            print(f"Error processing study {nct_id}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"Successfully processed {studies_processed} studies")
    print(f"Trials data written to: trials.csv")
    print(f"Locations data written to: locations.csv") 
    print(f"Conditions data written to: conditions.csv")
    print(f"Interventions data written to: interventions.csv")

except Exception as e:
    print(f"Error during file operations: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Ensure files are closed
    trials_file.close() if 'trials_file' in locals() else None
    locations_file.close() if 'locations_file' in locals() else None
    conditions_file.close() if 'conditions_file' in locals() else None
    interventions_file.close() if 'interventions_file' in locals() else None

print("\nProcess completed!")