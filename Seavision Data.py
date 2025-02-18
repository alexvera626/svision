import requests
import json
import base64
import logging
import boto3
import time
from datetime import datetime, timezone

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# GitHub Config (
GITHUB_REPO = "alexvera626/svision" 
GITHUB_FILE_PATH = "seavision_data.geojson"
GITHUB_BRANCH = "main"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"


#Token Securely from AWS Secrets Manager
def get_github_token():
    """Retrieves the GitHub token from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name="us-west-1")  
    try:
        response = client.get_secret_value(SecretId="GITHUB_TOKEN")
        if "SecretString" in response:
            secret_data = json.loads(response["SecretString"])
            return secret_data.get("GITHUB_TOKEN")  
    except Exception as e:
        logging.error(f"❌ Error retrieving GitHub token: {e}")
        return None

# Secure GitHub Token
GITHUB_TOKEN = get_github_token()
if not GITHUB_TOKEN:
    logging.error("❌ GitHub token could not be retrieved!")

# SeaVision API Configuration/key/To do use aws secrets managers
SEAVISION_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  
API_URL = "https://api.seavision.volpe.dot.gov/v1/vessels"
#2 keys more locations?
LOCATIONS = [
    {"latitude": 34.110038, "longitude": -119.209365, "radius": 100, "age": 1},
    {"latitude": 34.16182, "longitude": -120.27813, "radius": 100, "age": 1},
    {"latitude": 35.03000, "longitude": -122.23366, "radius": 100, "age": 1},
]

# Fetch vessel data from SeaVision API
def fetch_seavision_data():
    """Fetches vessel data from SeaVision API and converts it to GeoJSON."""
    headers = {"accept": "application/json", "x-api-key": SEAVISION_API_KEY}
    all_vessels = []

    for params in LOCATIONS:
        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code == 200:
            all_vessels.extend(response.json())
        else:
            logging.error(f"❌ API Error {response.status_code}: {response.text}")

    # Remove duplicates using 'mmsi' as a unique key
    unique_vessels = {v["mmsi"]: v for v in all_vessels}
    cleaned_vessels = list(unique_vessels.values())

    # Convert to GeoJSON format
    return {
        "type": "FeatureCollection",
        "name": "SeaVision Data",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [v["longitude"], v["latitude"]]},
                "properties": {
                    "name": v["name"],
                    "mmsi": v["mmsi"],
                    "imoNumber": v["imoNumber"],
                    "callSign": v["callSign"],
                    "cargo": v["cargo"],
                    "vesselType": v["vesselType"],
                    "COG": v["COG"],
                    "heading": v["heading"],
                    "navStatus": v["navStatus"],
                    "SOG": v["SOG"],
                    "timeOfFix": v["timeOfFix"],
                    "length": v["length"],
                    "beam": v["beam"],
                    "datePulled": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            }
            for v in cleaned_vessels
        ],
    }

# Fetch current file SHA from GitHub
def get_file_sha(headers):
    """Retrieves the SHA of the existing file for GitHub updates."""
    response = requests.get(GITHUB_API_URL, headers=headers)
    return response.json().get("sha") if response.status_code == 200 else None

# Upload data to GitHub
def upload_to_github(geojson_data):
    """Uploads or updates the SeaVision GeoJSON file in GitHub repository."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "SeaVision-Data-Bot",
    }

    json_data = json.dumps(geojson_data, indent=4)
    file_sha = get_file_sha(headers)

    payload = {
        "message": f"🔄 Auto-update SeaVision GeoJSON [{time.strftime('%Y-%m-%d %H:%M:%S')}]",
        "content": base64.b64encode(json_data.encode()).decode(),
        "branch": GITHUB_BRANCH,
        **({"sha": file_sha} if file_sha else {}),
    }

    response = requests.put(GITHUB_API_URL, headers=headers, json=payload)
    logging.info(f"📬 GitHub API Response: {response.status_code} - {response.text}")

#AWS Lambda Handler
def lambda_handler(event, context):
    """AWS Lambda entry point."""
    geojson_output = fetch_seavision_data()
    upload_to_github(geojson_output)
    return {"statusCode": 200, "body": "Success"}

