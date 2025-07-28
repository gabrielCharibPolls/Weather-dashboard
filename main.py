from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import httpx
import time
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import threading


load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_KEY = os.getenv("API_KEY")
API_URL = "http://api.weatherapi.com/v1/current.json"
DATA_FILE = "weather_history.json"
CITY = "Kraainem"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def save_measure(city: str, temperature: float, humidity: int):
    date_str = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if city not in data:
        data[city] = []

    data[city].append({
        "date": date_str,
        "temperature": temperature,
        "humidity": humidity
    })

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def fetch_weather_data_and_save(city: str):
    url = f"{API_URL}?key={API_KEY}&q={city}&lang=fr"
    response = httpx.get(url)

    if response.status_code == 200:
        current = response.json()["current"]
        temperature = current["temp_c"]
        humidity = current["humidity"]
        save_measure(city, temperature, humidity)

def background_fetch_weather():
    while True:
        fetch_weather_data_and_save(CITY)
        time.sleep(3600)



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    threading.Thread(target=background_fetch_weather, daemon=True).start()
app = FastAPI(lifespan=lifespan)  

@app.get("/", response_class=HTMLResponse)
async def fetch_weather(request: Request, city: str = CITY):
    with open(DATA_FILE, "r") as f:
        history = json.load(f)
    return templates.TemplateResponse("history.html", {
        "request": request,
        "city": city,
        "history": history.get(city, [])
    })
