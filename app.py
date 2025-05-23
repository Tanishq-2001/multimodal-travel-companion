import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import wikipedia
import requests
import os
import spacy
from geopy.geocoders import Nominatim

# Load models once
@st.cache_resource
def load_models():
    blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    spacy_model = spacy.load("en_core_web_sm")
    return blip_processor, blip_model, spacy_model

# Get caption from image
def get_caption(image_path, processor, model):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

# Extract city from caption
def extract_city_from_caption(caption, nlp):
    caption_lower = caption.lower()

    known_mappings = {
        "statue of liberty": "New York",
        "eiffel tower": "Paris",
        "taj mahal": "Agra",
        "big ben": "London",
        "colosseum": "Rome",
        "christ the redeemer": "Rio de Janeiro",
        "sydney opera house": "Sydney",
        "burj khalifa": "Dubai",
        "gateway of india": "Mumbai",
        "denver": "Denver",
        "new york": "New York",
        "paris": "Paris",
        "tokyo": "Tokyo",
        "rome": "Rome",
        "london": "London",
        "sydney": "Sydney",
        "rio de janeiro": "Rio de Janeiro",
        "chicago": "Chicago",
        "washington": "Washington D.C.",
        "boston": "Boston",
        "seattle": "Seattle"
    }

    for keyword, city in known_mappings.items():
        if keyword in caption_lower:
            return city

    doc = nlp(caption)
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            return ent.text

    try:
        geolocator = Nominatim(user_agent="travel-companion")
        location = geolocator.geocode(caption)
        if location:
            return location.address.split(",")[0]
    except:
        pass

    return "Unknown"

# Wikipedia summary
def get_landmark_info(landmark):
    try:
        return wikipedia.summary(landmark, sentences=3)
    except:
        return "No information found."

# OpenWeatherMap call
def get_weather(city_name, api_key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if "weather" in data and "main" in data:
            desc = data['weather'][0]['description']
            temp = data['main']['temp']
            return desc, temp
    except:
        pass
    return "Unavailable", "-"

# Google Places API
def get_nearby_places(city_name, api_key):
    try:
        geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}"
        geo_data = requests.get(geo_url).json()
        loc = geo_data["results"][0]["geometry"]["location"]
        lat, lon = loc["lat"], loc["lng"]

        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=2000&type=tourist_attraction&key={api_key}"
        places_data = requests.get(places_url).json()
        return [place["name"] for place in places_data.get("results", [])[:5]]
    except:
        return ["Location not found"]

# --- Streamlit App Starts ---
st.set_page_config(page_title="Multimodal Travel Companion", layout="centered")
st.title("🌍 Multimodal Travel Companion")
st.markdown("Upload a landmark photo to get history, weather, and nearby attractions.")

uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded:
    path = "uploaded_image.jpg"
    with open(path, "wb") as f:
        f.write(uploaded.read())

    st.image(path, caption="Your Upload", use_container_width=True)

    processor, blip_model, spacy_model = load_models()
    with st.spinner("Detecting landmark..."):
        guess = get_caption(path, processor, blip_model)
        st.success(f"🔍 Model guess: {guess}")

    caption = st.text_input(
        "Detected landmark (you can correct it below if it’s too vague or wrong):",
        value=guess,
        help="This affects what information we can retrieve (weather, attractions, etc.)"
    )

    if not caption.strip():
        st.warning("Please enter a landmark name to continue.")
        st.stop()

    city_name = extract_city_from_caption(caption, spacy_model)

    if city_name == "Unknown":
        city_name = st.text_input(
            "We couldn’t auto-detect a city. Please enter one to continue:",
            placeholder="e.g. Denver, Paris, Tokyo"
        )
        if not city_name.strip():
            st.warning("City is required to fetch weather and attractions.")
            st.stop()

    st.markdown(f"**About {caption}:**")
    with st.spinner("Fetching info..."):
        info = get_landmark_info(caption)
        st.write(info)

    weather_key = st.secrets.get("weather_key") or os.getenv("OPENWEATHER_API_KEY")
    places_key = st.secrets.get("google_places_key") or os.getenv("GOOGLE_PLACES_API_KEY")

    if weather_key:
        with st.spinner("Fetching weather..."):
            desc, temp = get_weather(city_name, weather_key)
            st.markdown(f"**Weather in {city_name}:** {desc}, {temp}°C")
    else:
        st.warning("Weather API key not set.")

    if places_key:
        with st.spinner("Fetching attractions..."):
            places = get_nearby_places(city_name, places_key)
            st.markdown("**Top Nearby Attractions:**")
            for p in places:
                st.markdown(f"- {p}")
    else:
        st.warning("Google Places API key not set.")
