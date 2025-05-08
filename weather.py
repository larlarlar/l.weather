from flask import Flask, request, render_template
import os
import requests

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@app.route("/", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            weather_data = get_weather(city)
            return render_template("weather.html", weather=weather_data, city=city)
    
    return render_template("weather.html")

def get_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"  # Для получения данных на русском
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка запроса: {str(e)}"}
    except (KeyError, IndexError):
        return {"error": "Ошибка обработки данных"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))