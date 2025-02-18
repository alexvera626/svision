import os
import requests
import json
import csv
from datetime import datetime, timezone

# Fetch the SeaVision API key from the environment
api_key = os.getenv('SEAVISION_API_KEY')

if api_key is None:
    raise ValueError("API key is missing!")  # Ensure the API key is present

# API URL and Parameters for 3 locations
api_url = 'https://api.seavision.volpe.dot.gov/v1/vessels'

# Parameters for the 3 different API calls
params_list = [
    {'latitude': 34.110038, 'longitude': -119.209365, 'radius': 100, 'age': 1},
    {'latitude': 34.16182, 'longitude': -120.27813, 'radius': 100, 'age': 1},
    {'latitude': 35.03000, 'longitude': -122.23366, 'radius': 100, 'age': 1},
]

# Headers for the API request
headers = {
    'accept': 'application/json',
    'x-api-key': api_key
}

# List to hold all vessel data
all_vessels = []

# Function to make the API call and get data
def fetch_data(params):
    response = requests.get(api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()  # Return JSON data
    else:
        print(f"Failed to fetch data for {params['latitude']}, {params['longitude']}. Status code: {response.status_code}")
        return []

# Get current date and time in UTC (Zulu format) using timezone-aware datetime
current_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# Loop through the list of parameters and fetch data
for params in params_list:
    print(f"Fetching data for {params['latitude']}, {params['longitude']}")
    data = fetch_data(params)
    all_vessels.extend(data)  # Add the vessels from this call to the list

# Remove duplicates based on the 'mmsi' field
unique_vessels = {}
for vessel in all_vessels:
    unique_vessels[vessel['mmsi']] = vessel  # Using MMSI as a unique key

# Now 'unique_vessels' contains only unique vessels
cleaned_vessels = list(unique_vessels.values())

# Convert to GeoJSON format
geojson = {
    "type": "FeatureCollection",
    "name": "SeaVision Data",
    "features": []
}

# Add each vessel as a feature in the GeoJSON
for vessel in cleaned_vessels:
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [vessel['longitude'], vessel['latitude']]
        },
        "properties": {
            "name": vessel['name'],
            "mmsi": vessel['mmsi'],
            "imoNumber": vessel['imoNumber'],
            "callSign": vessel['callSign'],
            "cargo": vessel['cargo'],
            "vesselType": vessel['vesselType'],
            "COG": vessel['COG'],
            "heading": vessel['heading'],
            "navStatus": vessel['navStatus'],
            "SOG": vessel['SOG'],
            "timeOfFix": vessel['timeOfFix'],
            "length": vessel['length'],
            "beam": vessel['beam'],
            "datePulled": current_time,  # Added the datePulled field in Zulu format
        }
    }
    geojson["features"].append(feature)

# Save the GeoJSON data to a file inside the docs folder
geojson_file = 'docs/SeaVision_Data.geojson'  # Ensure it's saved in the 'docs' folder
with open(geojson_file, 'w') as f:
    json.dump(geojson, f, indent=4)

print(f"GeoJSON file has been saved as {geojson_file}")

# Save the CSV data to a file inside the docs folder
#csv_file = 'docs/SeaVision_Data.csv'

# Open CSV file to write
#with open(csv_file, mode='w', newline='') as csvfile:
#    writer = csv.writer(csvfile)
    
    # Write CSV header (columns based on GeoJSON properties)
#    writer.writerow([
#        'name', 'mmsi', 'imoNumber', 'callSign', 'cargo', 'vesselType', 
#        'COG', 'heading', 'navStatus', 'SOG', 'timeOfFix', 'length', 'beam', 'latitude', 'longitude', 'datePulled'
#    ])
    
    # Loop through GeoJSON features and write to CSV
    for vessel in cleaned_vessels:
        # Extract properties and coordinates
        properties = vessel
        coordinates = [vessel['longitude'], vessel['latitude']]
        
        # Write a row for each feature in the GeoJSON
        writer.writerow([
            properties['name'],
            properties['mmsi'],
            properties['imoNumber'],
            properties['callSign'],
            properties['cargo'],
            properties['vesselType'],
            properties['COG'],
            properties['heading'],
            properties['navStatus'],
            properties['SOG'],
            properties['timeOfFix'],
            properties['length'],
            properties['beam'],
            coordinates[1],  # latitude
            coordinates[0],  # longitude
            current_time     # using current date and time pulled
        ])

print(f"CSV file has been saved as {csv_file}")
