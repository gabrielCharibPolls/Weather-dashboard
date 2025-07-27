from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import json
import os
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_KEY = "57785c3ee536429cb7e155613252107"
API_URL = "http://api.weatherapi.com/v1/current.json"
DATA_FILE = "weather_history.json"


def save_measure(city: str, temperature: float, humidity: int):
    """Ajoute une mesure journalière dans le fichier JSON sans écraser l'existant"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    if city not in data:
        data[city] = []

    # Évite de dupliquer la date
    already_saved = any(entry["date"] == date_str for entry in data[city])
    if not already_saved:
        data[city].append({
            "date": date_str,
            "temperature": temperature,
            "humidity": humidity
        })

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.get("/", response_class=HTMLResponse)
async def fetch_weather(request: Request, city: str = "Kraainem"):
    url = f"{API_URL}?key={API_KEY}&q={city}&lang=fr"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        data = response.json()
        current = data["current"]
        temperature = current["temp_c"]
        humidity = current["humidity"]

        save_measure(city, temperature, humidity)

        with open(DATA_FILE, "r") as f:
            history = json.load(f)

        return templates.TemplateResponse("history.html", {
            "request": request,
            "city": city,
            "history": history.get(city, [])
        })
    else:
        return templates.TemplateResponse("history.html", {
            "request": request,
            "city": city,
            "history": [],
            "error": "Impossible de récupérer les données météo."
        })
