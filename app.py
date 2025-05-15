import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import wikipedia
import requests
import os
from places_api import get_nearby_places

# ——— Load BLIP model once ———
@st.cache_resource
def load_blip_model():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

def get_caption(image_path, processor, model):
    raw_image = Image.open(image_path).convert("RGB")
    inputs = processor(raw_image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

def get_landmark_info(landmark):
    try:
        return wikipedia.summary(landmark, sentences=3)
    except:
        return "No information found."

def get_weather(city_name, api_key):
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city_name}&appid={api_key}&units=metric"
        )
        data = requests.get(url).json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return weather, temp
    except:
        return "Unavailable", "-"

# ——— Streamlit UI ———
st.set_page_config(page_title="Multimodal Travel Companion", layout="centered")
st.title("🌍 Multimodal Travel Companion")
st.markdown("Upload a landmark photo to get history, weather, and nearby attractions.")

# File uploader
uploaded = st.file_uploader("Upload an image", type=["jpg","jpeg","png"])
if uploaded:
    path = "uploaded_image.jpg"
    with open(path, "wb") as f:
        f.write(uploaded.read())
    st.image(path, caption="Your Upload", use_container_width=True)

    # Caption step
    processor, model = load_blip_model()
    with st.spinner("Detecting landmark..."):
        guess = get_caption(path, processor, model)
        st.success(f"🔍 Model guess: {guess}")

    # Allow manual correction
    caption = st.text_input("Edit landmark name (optional)", value=guess)

    # City input
    city_name = st.text_input("City for weather/places", value="Charlotte")

    # Wikipedia info
    with st.spinner("Fetching info..."):
        info = get_landmark_info(caption)
        st.markdown(f"**About {caption}:**\n\n{info}")

    # Weather
    weather_key = (st.secrets.get("weather_key") or os.getenv("OPENWEATHER_API_KEY"))
    if weather_key:
        with st.spinner("Fetching weather..."):
            weather, temp = get_weather(city_name, weather_key)
            st.markdown(f"**Weather in {city_name}:** {weather}, {temp}°C")
    else:
        st.warning("OpenWeather key not set.")

    # Nearby attractions
    places_key = (st.secrets.get("google_places_key") or os.getenv("GOOGLE_PLACES_API_KEY"))
    if places_key:
        with st.spinner("Finding nearby attractions..."):
            nearby = get_nearby_places(city_name, places_key)
            st.markdown("**Top Nearby Attractions:**")
            for p in nearby:
                st.markdown(f"- {p}")
    else:
        st.warning("Google Places key not set.")
