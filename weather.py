from flask import Flask
app = Flask(__name__)  # обязательно назвать переменную `app`

@app.route("/")
def hello():
    return "Weather App! 🌦️"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

import requests

API_KEY = "your_api_key"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"Temperature: {data['main']['temp']}°C")
    else:
        print("Error of request!")