import requests
import os

def get_nearby_places(city, api_key):
    # Geocode the city name to lat/lon
    geocode_url = (
        f"https://maps.googleapis.com/maps/api/geocode/json"
        f"?address={city}&key={api_key}"
    )
    geo_res = requests.get(geocode_url).json()
    if not geo_res.get("results"):
        return ["Location not found"]

    loc = geo_res["results"][0]["geometry"]["location"]
    lat, lon = loc["lat"], loc["lng"]

    # Query nearby tourist attractions
    places_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lon}"
        f"&radius=2000"
        f"&type=tourist_attraction"
        f"&key={api_key}"
    )
    places_res = requests.get(places_url).json()
    results = places_res.get("results", [])
    return [place["name"] for place in results[:5]] or ["No attractions found"]
