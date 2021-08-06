from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

@app.get("/locations")
def get_all_locations():
    return {}

@app.get("/locations/{lat},{long},{radius}")
def get_nearby_locations(lat: float, long: float, radius: float):
    return {}
