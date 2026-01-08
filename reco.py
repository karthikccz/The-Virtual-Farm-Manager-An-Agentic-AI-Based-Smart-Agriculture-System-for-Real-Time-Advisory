

import requests

def get_weather(city: str, api_key: str):
    """Fetch real-time weather data safely."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # catches 401, 403, 404

        data = response.json()

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rain": "rain" in data,
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "source": "live"
        }

    except Exception as e:
        return {
            "temperature": None,
            "humidity": None,
            "rain": False,
            "wind_speed": None,
            "description": "Unavailable",
            "source": "offline",
            "error": str(e)
        }
print(get_weather("Adilabad", "22add7525c95278176e23268d8fd34ab"))


def recommendation_agent(agent1, agent2, agent3, weather):
    advice = []

    # -----------------------------
    # Crop Health Logic
    # -----------------------------
    if agent2["health_status"] == "Diseased_moderate":
        advice.append(
            "⚠️ Moderate disease detected. Apply recommended fungicide or bactericide immediately "
            "and remove heavily infected leaves to prevent spread."
        )
    elif agent2["health_status"] == "Diseased_mild":
        advice.append(
            "🩺 Mild disease detected. Apply preventive spray and continue monitoring crop health."
        )
    else:
        advice.append("✅ Crop health is good. Maintain regular monitoring and nutrition.")

    # -----------------------------
    # Weather-based Risk
    # -----------------------------
    if weather.get("source") == "live":
        if weather["humidity"] > 70 and weather["rain"]:
            advice.append(
                "🌧️ High humidity and rainfall increase disease risk. Avoid irrigation and apply protective fungicide."
            )
        if weather["temperature"] > 35:
            advice.append(
                "🌡️ High temperature detected. Avoid spraying during midday; spray early morning or evening."
            )
    else:
        advice.append("⚠️ Weather data unavailable. Advice based on crop and market conditions only.")

    # -----------------------------
    # Field Condition
    # -----------------------------
    if agent1["weed_percentage"] > 20:
        advice.append(
            "🌿 High weed infestation detected. Mechanical weeding or selective herbicide application is advised."
        )

    # -----------------------------
    # Market Insight
    # -----------------------------
    advice.append(f"📈 Market insight: {agent3['recommendation']}")

    # -----------------------------
    # DETAILED FINAL DECISION (ENHANCED)
    # -----------------------------
    decision_parts = []

    # Weather influence
    if weather.get("source") == "live":
        decision_parts.append(
            f"The current weather shows a temperature of {weather['temperature']}°C "
            f"with {weather['humidity']}% humidity and {weather['description']} conditions."
        )

        if weather["rain"]:
            decision_parts.append(
                "Rainfall increases the risk of disease spread and post-harvest losses."
            )
        else:
            decision_parts.append(
                "Dry weather conditions are favorable for crop protection and harvesting activities."
            )

    # Crop health influence
    if agent2["health_status"] == "Diseased_mild":
        decision_parts.append(
            "Since the disease level is mild, timely preventive treatment can restore crop health."
        )
    elif agent2["health_status"] == "Diseased_moderate":
        decision_parts.append(
            "Due to moderate disease severity, immediate treatment is critical before harvest."
        )
    else:
        decision_parts.append(
            "The crop is healthy, which supports better yield and market quality."
        )

    # Weed influence
    if agent1["weed_percentage"] > 20:
        decision_parts.append(
            "Weed pressure is high and should be controlled to avoid yield reduction."
        )

    # Market influence
    if "WAIT" in agent3["recommendation"]:
        decision_parts.append(
            "Market trends indicate rising prices, so delaying harvest may increase profitability."
        )
    else:
        decision_parts.append(
            "Market prices may decline, so early harvest and selling is advisable."
        )

    final_decision = " ".join(decision_parts)

    return {
        "crop": agent3.get("crop", "Unknown"),
        "best_mandi": agent3.get("best_mandi", "Not available"),
        "expected_price": agent3.get("predicted_price", "N/A"),
        "weather_summary": weather,
        "detailed_advice": advice,
        "final_recommendation": final_decision
    }


