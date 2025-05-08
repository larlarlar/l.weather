from flask import Flask, request, render_template, redirect, url_for, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
API_KEY = os.getenv("OPENWEATHER_API_KEY")

@app.route("/", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        if 'clear' in request.form:
            session.pop('last_city', None)
            session.pop('weather_data', None)
            return redirect(url_for('weather'))
        city = request.form.get("city", "").strip()
        if city:
            session['last_city'] = city
            return redirect(url_for('weather_results'))
    
    return render_template("weather.html", 
                         city=session.get('last_city', ""),
                         weather=session.get('weather_data'))

@app.route("/results")
def weather_results():
    city = session.get('last_city', "")
    if not city:
        return redirect(url_for('weather'))
    
    weather_data = get_weather(city)
    if "error" in weather_data:
        session['weather_data'] = None
        return render_template("weather.html",
                            city=city,
                            error=weather_data["error"])
    
    session['weather_data'] = weather_data
    return render_template("weather.html",
                         weather=weather_data,
                         city=city)



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
                "lang": "eng"
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
    
    # GET request or empty form submission
    return render_template("weather.html", 
                         weather=None, 
                         city=city,
                         error=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))