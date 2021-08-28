import logging
import pprint
import uuid

import uvicorn
from fastapi import FastAPI, Response, status, File, UploadFile, Form, Depends

# import LocationService
# import SpeciesService
# import UserService
# import CouncilService
# import WeedInstanceService

# from DatabaseService import *
# from SpeciesService import *
# from CouncilService import *

from typing import *
from db.database import database
from Models.Person import Person
from Models.WeedInstance import WeedInstance
from Models.Location import Location
from Models.Species import Species
from Models.Council import Council
from Models.GeoJSONPoint import GeoJSONPoint

from routers import councils
from routers import persons
from routers import locations 
from routers import species 
from routers import persons 
from routers import weeds 

app = FastAPI()

p = pprint.PrettyPrinter()
log = logging.getLogger("backend-logger")

@app.on_event("startup")
async def startup():
    app.state.db = database().get_client()

app.include_router(councils.router)
app.include_router(locations.router)
app.include_router(persons.router)
app.include_router(species.router)
# app.include_router(weeds.router)

# SETUP UNIQUE KEYS
# LocationService.set_unique_keys(locations_collection)
# CouncilService.set_unique_keys(councils_collection)
# WeedInstanceService.set_unique_keys(weeds_collection)


@app.post("/weeds/add")
async def add_weed(weed_id: int, discovery_date: str, removed: bool, 
                        removal_date: Optional[str], replaced: bool, replaced_species: Optional[str], 
                        image_filename: Optional[str], file: UploadFile = File(...)):
    """Adds a weed instance"""
    # -- async def upload(user: User = Depends(), file: UploadFile = File(...)):

    weed = WeedInstance({"weed_id": weed_id, "discovery_date": discovery_date, 
                "removed": removed, "removal_date": removal_date, "replaced": replaced, 
                "replaced_species": replaced_species, "image_filename": image_filename})

    return WeedInstanceService.add_weed(weeds_collection, weed, file)

@app.post("/weeds/tstfile")
async def create_file(
    fileb: UploadFile = File(...), token: str = Form(...)
):
    # print(len(fileb.file_size))
    # print(fileb)
    print(token)
    print(fileb.content_type)
    return {
        "file_size": len(fileb),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }

if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8080, reload=True)
