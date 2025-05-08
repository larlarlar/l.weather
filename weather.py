from flask import Flask, request, render_template
import os
import requests

app = Flask(__name__)
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Basic
@app.route("/", methods=["GET", "POST"])
def weather():
    error = None
    weather_data = None
    city = ""
    
    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            weather_data = get_weather(city)
            if "error" in weather_data:
                error = weather_data["error"]
            elif weather_data.get("cod") == "404":  # City is not found
                error = f"City '{city}' is not found. Check the name, please. Check that city name is written in English"
    
    return render_template("weather.html", 
                         weather=weather_data, 
                         city=city, 
                         error=error)

# Getting weather info
def get_weather(city):
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric",
                "lang": "ru"
            },
            timeout=10  # timout 10 sec
        )
        data = response.json()
        
        # Processing API errors
        if data.get("cod") != 200:
            return {
                "cod": data.get("cod"),
                "error": data.get("message", "Unknown API error")
            }
            
        return {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "city": data["name"]
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}
    except (KeyError, IndexError):
        return {"error": "Processing error"}
    except ValueError:
        return {"error": "Invalid text"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))