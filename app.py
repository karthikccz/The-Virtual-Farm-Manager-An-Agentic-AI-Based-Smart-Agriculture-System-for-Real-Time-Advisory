import streamlit as st
import tempfile
import numpy as np
import cv2

from agent1 import run_agent1
from agent2 import run_agent2
from agent3 import run_agent3
from reco import recommendation_agent, get_weather

import os


def card(title, content, color="#f9f9f9"):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:18px;
            border-radius:12px;
            margin-bottom:15px;
            box-shadow:0px 2px 6px rgba(0,0,0,0.08);
        ">
            <h4>{title}</h4>
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------
# LANGUAGE TRANSLATIONS
# ---------------------------
LANG = {
    "English": {
        "title": "🌾 Virtual Farm Manager (Agentic AI)",
        "caption": "AI-powered decision support for Smart Agriculture",
        "upload_field": "📷 Upload Field Image (Drone / Satellite)",
        "upload_leaf": "🍃 Upload Leaf Image (Crop Health)",
        "crop": "🌱 Crop Name",
        "city": "🌦️ City for Weather",
        "run": "🚀 Get Smart Recommendation",
        "final": "✅ Final Recommendation",
        "advice": "📋 Detailed Advice",
        "decision": "🧠 Final Decision",
        "weather": "🌦️ Weather Summary",
    },

    "Hindi": {
        "title": "🌾 वर्चुअल फार्म मैनेजर",
        "caption": "स्मार्ट कृषि के लिए AI आधारित निर्णय प्रणाली",
        "upload_field": "📷 खेत की तस्वीर अपलोड करें",
        "upload_leaf": "🍃 पत्ते की तस्वीर अपलोड करें",
        "crop": "🌱 फसल का नाम",
        "city": "🌦️ मौसम के लिए शहर",
        "run": "🚀 सिफारिश प्राप्त करें",
        "final": "✅ अंतिम सिफारिश",
        "advice": "📋 विस्तृत सुझाव",
        "decision": "🧠 अंतिम निर्णय",
        "weather": "🌦️ मौसम विवरण",
    },

    "Telugu": {
        "title": "🌾 వర్చువల్ ఫార్మ్ మేనేజర్",
        "caption": "స్మార్ట్ వ్యవసాయానికి AI ఆధారిత నిర్ణయ వ్యవస్థ",
        "upload_field": "📷 పొలపు చిత్రం అప్లోడ్ చేయండి",
        "upload_leaf": "🍃 ఆకుల చిత్రం అప్లోడ్ చేయండి",
        "crop": "🌱 పంట పేరు",
        "city": "🌦️ వాతావరణం కోసం నగరం",
        "run": "🚀 సిఫార్సు పొందండి",
        "final": "✅ తుది సిఫార్సు",
        "advice": "📋 వివరమైన సూచనలు",
        "decision": "🧠 తుది నిర్ణయం",
        "weather": "🌦️ వాతావరణ సమాచారం",
    }
}


# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Virtual Farm Manager",
    page_icon="🌾",
    layout="wide"
)

# ---------------------------
# LANGUAGE SELECTOR
# ---------------------------
language = st.selectbox(
    "🌐 Select Language / భాష ఎంచుకోండి / भाषा चुनें",
    ["English", "Hindi", "Telugu"]
)

T = LANG[language]


st.title(T["title"])
st.caption(T["caption"])

st.markdown("---")

# ---------------------------
# USER INPUT
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    field_image = st.file_uploader(
        T["upload_field"],
        type=["jpg", "jpeg", "png"]
    )

with col2:
    leaf_image = st.file_uploader(
        T["upload_leaf"],
        type=["jpg", "jpeg", "png"]
    )   

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    crop_name = st.text_input(T["crop"], placeholder="Tomato / Potato / Onion")

with col4:
    city = st.text_input(T["city"], value="Adilabad")

api_key = st.text_input(
    "🔑 OpenWeather API Key (optional)",
    type="password"
)

st.markdown("---")


# ---------------------------
# RUN PIPELINE
# ---------------------------
if st.button("🚀 Get Smart Recommendation"):
    if not field_image or not leaf_image:
        st.error("Please upload both field image and leaf image.")
        st.stop()

    if not crop_name or not city:
        st.error("Please enter crop name and city.")
        st.stop()

    # Save uploaded files
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f1:
        f1.write(field_image.read())
        field_path = f1.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f2:
        f2.write(leaf_image.read())
        leaf_path = f2.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f3:
        annotated_path = f3.name

    # Run agents
    with st.spinner("🔍 Analyzing field condition..."):
        agent1_output = run_agent1(field_path, save_annotated=annotated_path)

    with st.spinner("🧪 Analyzing crop health..."):
        agent2_output = run_agent2(leaf_path)

    with st.spinner("📈 Analyzing market prices..."):
        agent3_output = run_agent3(crop_name)

    with st.spinner("🌦️ Fetching weather..."):
        weather = get_weather(city, api_key) if api_key else {
            "source": "unavailable",
            "rain": False
        }

    final_output = recommendation_agent(
        agent1_output,
        agent2_output,
        agent3_output,
        weather
    )

    # ---------------------------
    # DISPLAY RESULTS
    # ---------------------------
    st.markdown(f"## {T['final']}")

    colA, colB = st.columns(2)

    with colA:
        st.image(
            annotated_path,
            caption="Field Analysis Output",
            use_container_width=True
        )

    with colB:
        st.metric("🌱 Crop", final_output["crop"])
        st.metric("🏬 Best Mandi", final_output["best_mandi"])
        st.metric("💰 Expected Price", f"₹{final_output['expected_price']} / quintal")
        st.metric("🍃 Crop Health", agent2_output["health_status"])

    advice_html = "<ul>" + "".join(
    [f"<li>{tip}</li>" for tip in final_output["detailed_advice"]]
) + "</ul>"

    card("📋 Detailed Advice", advice_html, "#eef6ff")



    st.markdown(f"### {T['weather']}")
    w = final_output["weather_summary"]

    weather_text = f"""
    🌡️ Temperature: {w.get('temperature')} °C  
    💧 Humidity: {w.get('humidity')} %  
    🌬️ Wind Speed: {w.get('wind_speed')} m/s  
    🌧️ Rain Expected: {"Yes" if w.get("rain") else "No"}  
    ☁️ Condition: {w.get("description", "N/A")}
"""

    card("🌦️ Weather Summary", weather_text, "#f0fff4")


    st.markdown(f"### {T['decision']}")
    card(
    "🧠 Final Decision",
    f"<b>{final_output['final_recommendation']}</b>",
    "#e6fffa"
)

    
    # -------------------------------
    # CLEANUP (FIXED INDENTATION)
    # -------------------------------
    os.remove(field_path)
    os.remove(leaf_path)
    os.remove(annotated_path)
