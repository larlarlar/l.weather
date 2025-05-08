from flask import Flask, request, render_template
import os
import requests

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key")  # Use environment variables
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@app.route("/", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            weather_data = get_weather(city)
            return render_template("weather.html", weather=weather_data, city=city)
    
    return render_template("weather.html", weather=None)

def get_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "en"  # English language response
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raises exception for 4XX/5XX errors
        data = response.json()
        
        # Check if required fields exist
        if not all(key in data for key in ['main', 'weather']):
            return {"error": "Incomplete weather data received"}
            
        return {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].capitalize(),
            "icon": data["weather"][0]["icon"],
            "wind_speed": data.get("wind", {}).get("speed", "N/A")
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except (KeyError, IndexError, TypeError) as e:
        return {"error": f"Data processing error: {str(e)}"}
    except ValueError as e:  # JSON decode error
        return {"error": "Invalid API response format"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))