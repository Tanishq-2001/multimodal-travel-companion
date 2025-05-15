# 🌍 Multimodal Travel Companion

An AI-powered tool that lets you upload a photo of a landmark and instantly:
- Detects the landmark (via vision-language models)
- Fetches historical facts from Wikipedia
- Shows live weather in that location
- Lists top tourist attractions nearby using Google Places API

---

## 🔍 Features
- **BLIP model** for image captioning (landmark detection)
- **Wikipedia integration** for quick historical context
- **OpenWeatherMap API** for real-time weather info
- **Google Places API** to discover nearby places
- **Streamlit app** for smooth user experience

---

## 🚀 Demo
(You can deploy to [Streamlit Cloud](https://streamlit.io/cloud) and paste the link here)

---

## 🧠 How It Works
1. User uploads an image
2. BLIP model generates a caption (editable by user)
3. City is specified for improved context
4. App calls:
   - Wikipedia → for landmark description
   - OpenWeather → for weather
   - Google Places → for tourist spots

---

## 🛠 Tech Stack
- `streamlit`
- `transformers` (BLIP by Salesforce)
- `wikipedia` Python package
- `requests` for API integration

---

## 🔑 Setup Locally

```bash
git clone https://github.com/yourusername/multimodal-travel-companion
cd multimodal-travel-companion
pip install -r requirements.txt
