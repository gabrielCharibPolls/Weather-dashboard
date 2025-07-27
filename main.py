from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import json
import os
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")
#############################
#
#########################################
API_KEY = "57785c3ee536429cb7e155613252107"
API_URL = "http://api.weatherapi.com/v1/current.json"
DATA_FILE = "weather_history.json"
CITY = "Kraainem"



if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)  


def fetch_weather_data_and_save(city: str):
    response = httpx.get(f"{API_URL}?key={API_KEY}&q={city}&lang=fr")
    """Récupère les données météo pour une ville donnée"""
    url = f"{API_URL}?key={API_KEY}&q={city}&lang=fr"
    response = httpx.get(url)

    if response.status_code == 200:
        response = response.json()
        temperature = response.data["current"]["temp_c"]
        humidity = response.data["current"]["humidity"]
        save_measure(city, temperature, humidity)
        return response.json()

    else:
        return None


def save_measure(city: str, temperature: float, humidity: int):
    """Ajoute une mesure journalière dans le fichier JSON sans écraser l'existant"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.get("/", response_class=HTMLResponse)
async def fetch_weather(request: Request, city: str = CITY):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            history = json.load(f)
    else:
        history = {}
    return templates.TemplateResponse("history.html", {
        "request": request,
        "city": city,
        "history": history.get(city, [])
    })