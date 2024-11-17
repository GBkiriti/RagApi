import os
import pandas as pd
import googlemaps
from geopy.distance import geodesic

# Initialize Google Maps API client
API_KEY = 'Ask ME'  # Replace with your actual API key
gmaps = googlemaps.Client(key=API_KEY)

# Comprehensive list of sea coasts in India
sea_coasts = [
    {"name": "Dwarka Coast (Gujarat)", "lat": 22.2395, "lon": 68.9670},
    {"name": "Porbandar Coast (Gujarat)", "lat": 21.6417, "lon": 69.6293},
    {"name": "Veraval Coast (Gujarat)", "lat": 20.9034, "lon": 70.3676},
    {"name": "Mumbai Coast (Maharashtra)", "lat": 18.975, "lon": 72.825},
    {"name": "Ratnagiri Coast (Maharashtra)", "lat": 16.9902, "lon": 73.3120},
    {"name": "Alibag Coast (Maharashtra)", "lat": 18.6414, "lon": 72.8724},
    {"name": "Panaji Coast (Goa)", "lat": 15.4909, "lon": 73.8278},
    {"name": "Vasco da Gama Coast (Goa)", "lat": 15.3958, "lon": 73.8157},
    {"name": "Mangalore Coast (Karnataka)", "lat": 12.9141, "lon": 74.8560},
    {"name": "Karwar Coast (Karnataka)", "lat": 14.8136, "lon": 74.1297},
    {"name": "Kochi Coast (Kerala)", "lat": 9.9312, "lon": 76.2673},
    {"name": "Thiruvananthapuram Coast (Kerala)", "lat": 8.5241, "lon": 76.9366},
    {"name": "Kollam Coast (Kerala)", "lat": 8.8932, "lon": 76.6141},
    {"name": "Kozhikode Coast (Kerala)", "lat": 11.2588, "lon": 75.7804},
    {"name": "Chennai Coast (Tamil Nadu)", "lat": 13.0827, "lon": 80.2707},
    {"name": "Tuticorin Coast (Tamil Nadu)", "lat": 8.7642, "lon": 78.1348},
    {"name": "Nagapattinam Coast (Tamil Nadu)", "lat": 10.7657, "lon": 79.8431},
    {"name": "Puducherry Coast (Puducherry)", "lat": 11.9139, "lon": 79.8145},
    {"name": "Visakhapatnam Coast (Andhra Pradesh)", "lat": 17.6868, "lon": 83.2185},
    {"name": "Kakinada Coast (Andhra Pradesh)", "lat": 16.9891, "lon": 82.2475},
    {"name": "Nellore Coast (Andhra Pradesh)", "lat": 14.4426, "lon": 79.9865},
    {"name": "Puri Coast (Odisha)", "lat": 19.8135, "lon": 85.8312},
    {"name": "Paradeep Coast (Odisha)", "lat": 20.3167, "lon": 86.6100},
    {"name": "Gopalpur Coast (Odisha)", "lat": 19.2686, "lon": 84.9126},
    {"name": "Digha Coast (West Bengal)", "lat": 21.6278, "lon": 87.5402},
    {"name": "Port Blair Coast (Andaman and Nicobar Islands)", "lat": 11.6234, "lon": 92.7265},
    {"name": "Havelock Island Coast (Andaman and Nicobar Islands)", "lat": 12.0246, "lon": 93.0113},
    {"name": "Kavaratti Coast (Lakshadweep Islands)", "lat": 10.5667, "lon": 72.6369}
]

# Function to get the state from coordinates using Google Maps API
def get_state_from_coordinates(lat, lon):
    try:
        result = gmaps.reverse_geocode((lat, lon))
        if result:
            for component in result[0]['address_components']:
                if 'administrative_area_level_1' in component['types']:
                    return component['long_name']
        return None
    except Exception as e:
        print(f"Error getting state for coordinates ({lat}, {lon}): {e}")
        return None

# Function to calculate distance to the nearest sea coast
def get_nearest_sea_coast(lat, lon):
    nearest_coast = None
    min_distance = float('inf')
    for coast in sea_coasts:
        distance = geodesic((lat, lon), (coast["lat"], coast["lon"])).km
        if distance < min_distance:
            min_distance = distance
            nearest_coast = coast["name"]
    return nearest_coast, min_distance

# Load city data from a CSV file
cities_df = pd.read_csv("./Cities.csv")

# Add new columns for state, nearest sea coast, and distance
cities_df["State"] = ""
cities_df["Nearest_Sea_Coast"] = ""
cities_df["Distance_to_Sea_Coast_km"] = 0.0

# Process each city to get the state and nearest sea coast distance
for index, row in cities_df.iterrows():
    lat, lon = row["lat"], row["lng"]
    
    # Get the state using Google Maps Geocoding API
    state = get_state_from_coordinates(lat, lon)
    cities_df.at[index, "State"] = state

    # Get the nearest sea coast and distance using Google Maps Distance Matrix API
    nearest_coast, distance = get_nearest_sea_coast(lat, lon)
    cities_df.at[index, "Nearest_Sea_Coast"] = nearest_coast
    cities_df.at[index, "Distance_to_Sea_Coast_km"] = distance

# Save the updated dataset to a new CSV file
output_file = "indian_cities_with_state_and_coast_data.csv"
cities_df.to_csv(output_file, index=False)
print(f"Dataset saved as {output_file}")