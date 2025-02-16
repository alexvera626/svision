import requests
import time
import json

# Hex codes to be used in the request
hex_codes = [
    'adfe10', 'adfe12', 'adfe15', 'adfe17', 'adfe18', 'adfe1a', 'adfe1b', 'adfe1c', 'ae109a', 
    'ae10c1', 'ae10e8', 'ae10e9', 'ae10ea', 'ae10eb', 'ae10ec', 'ae20c1', 'ae2125', 'ae2126', 
    'ae2237', 'ae2238', 'ae223a', 'ae223b', 'ae223c', 'ae223d', 'ae223e', 'ae223f', 'ae265b', 
    'ae265c', 'ae265d', 'ae265e', 'ae2660', 'ae2661', 'ae2662', 'ae2663', 'ae2664', 'ae2665', 
    'ae2666', 'ae2667', 'ae2668', 'ae266a', 'ae266b', 'ae266c', 'ae266d', 'ae266e', 'ae266f', 
    'ae2672', 'ae2673', 'ae2674', 'ae2675', 'ae2676', 'ae2677', 'ae2678', 'ae2679', 'ae267a', 
    'ae267b', 'ae267c', 'ae267e', 'ae267f', 'ae2680', 'ae2681', 'ae2682', 'ae2683', 'ae2684', 
    'ae2685', 'ae2686', 'ae2687', 'ae2688', 'ae2689', 'ae268a', 'ae268b', 'ae268c', 'ae268d', 
    'ae268e', 'ae268f', 'ae2690', 'ae2691', 'ae2692', 'ae2693', 'ae2694', 'ae2695', 'ae2696', 
    'ae2697', 'ae2698', 'ae2699', 'ae269a', 'ae269b', 'ae269c', 'ae269d', 'ae269e', 'ae269f', 
    'ae26a0', 'ae26a1', 'ae26a2', 'ae26a3', 'ae26a4', 'ae26a5', 'ae26a6', 'ae26a7', 'ae26a8', 
    'ae26a9', 'ae26aa', 'ae26ab', 'ae26ac', 'ae26ad', 'ae26ae', 'ae26af', 'ae26b0', 'ae26b1', 
    'ae26b2', 'ae26b3', 'ae26b4', 'ae26b5', 'ae26b6', 'ae26b7', 'ae26b8', 'ae26ba', 'ae26bb', 
    'ae26bc', 'ae26bd', 'ae26be', 'ae26bf', 'ae2708', 'ae2709', 'ae270a', 'ae272e', 'ae2730', 
    'ae27f2', 'ae27f3', 'ae27f4', 'ae27f5', 'ae27f6', 'ae27f7', 'ae27f8', 'ae27f9', 'ae27fa', 
    'ae27fb', 'ae27fc', 'ae27fe', 'ae27ff', 'ae2900', 'ae2901', 'ae2902', 'ae2903', 'ae2905', 
    'ae2906', 'ae2907', 'ae2908', 'ae2909', 'ae290a', 'ae290c', 'ae290d', 'ae290e', 'ae290f', 
    'ae2910', 'ae2911', 'ae2912', 'ae2913', 'ae2914', 'ae2915', 'ae2916', 'ae2917', 'ae2918', 
    'ae2919', 'ae291a', 'ae2bef', 'ae2bf0', 'ae2bf1', 'ae2bf2', 'ae4a4b', 'ae4a4c', 'ae4adf', 
    'ae4ae0', 'ae4ae1', 'ae4ae2', 'ae4ae3', 'ae4ae4', 'ae4ae5', 'ae4cf7', 'ae4dfe', 'ae4dff', 
    'ae4e00', 'ae4e01', 'ae4e02', 'ae4e03', 'ae509f', 'ae57d1', 'ae57d2', 'ae57d3', 'ae57d4', 
    'ae57d5', 'ae5deb', 'ae5dec', 'ae5ded', 'ae5dee', 'ae5def', 'ae6ce7', 'ae6ce8', 'ad60d8',
    'a2097b', 'a638d5'
]

# Combine hex codes into a single string separated by commas
hex_codes_str = ",".join(hex_codes)

# API URL
url = f"https://opendata.adsb.fi/api/v2/icao/{hex_codes_str}"

# Making the request
response = requests.get(url)

# Function to convert JSON data to GeoJSON
def convert_to_geojson(data):
    features = []
    for ac in data['ac']:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [ac['lon'], ac['lat']]
            },
            "properties": {
                "hex": ac.get('hex', 'N/A'),
                "flight": ac.get('flight', 'N/A'),
                "desc": ac.get('desc', 'N/A'),
                "operator": ac.get('ownOp', 'Unknown'),
                "altitude": ac.get('alt_baro', 'N/A'),
                "ground_speed": ac.get('gs', 'N/A'),
                "track": ac.get('track', 'N/A'),
                "squawk": ac.get('squawk', 'N/A'),
                "year": ac.get('year', 'N/A'),
                "category": ac.get('category', 'N/A'),
                "rssi": ac.get('rssi', 'N/A'),
                "messages": ac.get('messages', 'N/A')
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson

# Check for successful request
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Convert the data to GeoJSON
    geojson_data = convert_to_geojson(data)
    
    # Save the GeoJSON data to a file
    with open('output.geojson', 'w') as geojson_file:
        json.dump(geojson_data, geojson_file, indent=4)
    print("GeoJSON file saved as 'output.geojson'")

else:
    print(f"Error {response.status_code}: Unable to fetch data.")

# Delay for 1 second to respect rate limit
time.sleep(1)

