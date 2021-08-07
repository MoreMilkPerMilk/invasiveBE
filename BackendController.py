import json
from typing import *

import pymongo
from fastapi import FastAPI
from pydantic import BaseModel, Field
from pymongo import mongo_client
from Models.Location import Location
from Models.Species import Species
from Models.WeedInstance import WeedInstance
import uvicorn

app = FastAPI()

# @app.get("/locations", response_model=List[Location])
@app.get("/locations")
def get_all_locations():
    data = {"name": "brisbane", "lat": 1, "long": -1}
    added_id = locations.insert_one(data).inserted_id
    print(added_id)
    return added_id

@app.get("/locations/{lat},{long},{radius}")
def get_nearby_locations(lat: float, long: float, radius: float):
    return {}

@app.post("/location/put")
def new_location():
    return "done"

def connect_to_mongodb():
    with open('cred.json') as f:
        cred = json.load(f)
        user = cred['user']
        password = cred['password']
        url = cred['url']
        client = pymongo.MongoClient(url.replace('<password>', password))
        return client['data']

if __name__ == '__main__':
    client = connect_to_mongodb()
    locations = client['locations']
    species = client['species']
    weed_instances = client['weed_instances']
    uvicorn.run(app, host='0.0.0.0', port=8000)