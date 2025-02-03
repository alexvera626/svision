import requests
import json
from datetime import datetime, timezone

# API URL and Parameters for 3 locations
api_url = 'https://api.seavision.volpe.dot.gov/v1/vessels'
api_key = 'tDbmrW2Etn5FV6JY4yMMC5QW1dAstsDL2Pt15JvH'  # Your API key

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
output_file = 'docs/SeaVision_Data.geojson'  # Ensure it's saved in the 'docs' folder
with open(output_file, 'w') as f:
    json.dump(geojson, f, indent=4)

print(f"GeoJSON file has been saved as {output_file}")
