import logging
import uvicorn
from fastapi import FastAPI, Response, status, File, UploadFile, Form, Depends

from typing import *
from db.database import database

# 
# from Models.Person import Person
# from Models.WeedInstance import WeedInstance
# from Models.Location import Location
# from Models.Species import Species
# from Models.Council import Council
# from Models.GeoJSONPoint import GeoJSONPoint

from routers import communities
from routers import councils
from routers import persons
from routers import locations 
from routers import species 
from routers import persons 
from routers import weeds 
from routers import tasks

app = FastAPI()

log = logging.getLogger("backend-logger")

@app.on_event("startup")
async def startup():
    app.state.db = database().get_client()

app.include_router(communities.router)
app.include_router(tasks.router)
app.include_router(councils.router)
app.include_router(locations.router)
app.include_router(persons.router)
app.include_router(species.router)
app.include_router(weeds.router)

# SETUP UNIQUE KEYS
# LocationService.set_unique_keys(locations_collection)
# CouncilService.set_unique_keys(councils_collection)
# WeedInstanceService.set_unique_keys(weeds_collection)

if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8080, reload=True)
