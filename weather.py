from flask import Flask, request, render_template, redirect, url_for, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle clear button
        if 'clear' in request.form:
            session.pop('last_city', None)
            session.pop('weather_data', None)
            return redirect(url_for('index'))
        
        # Handle search
        city = request.form.get("city", "").strip()
        if city:
            session['last_city'] = city
            weather_data = get_weather(city)
            
            if "error" in weather_data:
                return render_template("weather.html",
                                    city=city,
                                    error=weather_data["error"])
            
            session['weather_data'] = weather_data
            return render_template("weather.html",
                                weather=weather_data,
                                city=city)
    
    # GET request or empty form
    return render_template("weather.html",
                         city=session.get('last_city', ""),
                         weather=session.get('weather_data'))

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
            timeout=10
        )
        data = response.json()
        
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