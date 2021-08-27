import logging
import pprint
import uuid

import uvicorn
from fastapi import FastAPI, Response, status, File, UploadFile, Form, Depends

import LocationService
import SpeciesService
import UserService
import CouncilService
import WeedInstanceService

from DatabaseService import *
from SpeciesService import *
from CouncilService import *

from typing import *
from db.database import database
from Models.Person import Person
from Models.WeedInstance import WeedInstance
from Models.Location import Location
from Models.Species import Species
from Models.Council import Council
from Models.GeoJSONPoint import GeoJSONPoint

from .routers import councils

app = FastAPI()

p = pprint.PrettyPrinter()
log = logging.getLogger("backend-logger")

@app.on_event("startup")
async def startup():
    app.state.db = database().get_client()

app.include_router(councils.router)

# SETUP UNIQUE KEYS
LocationService.set_unique_keys(locations_collection)
CouncilService.set_unique_keys(councils_collection)
WeedInstanceService.set_unique_keys(weeds_collection)

# @app.get("/locations", response_model=List[Location])
@app.get("/locations", response_model=List[Location])
def get_all_locations():
    """
    Return all locations that exist within the databases
    """
    return LocationService.get_all(locations_collection)

@app.get("/location/", response_model=Location)
def get_location_by_id(location_id: int = None):
    """Gets a location by id"""
    if location_id is None:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    return LocationService.get_by_id(locations_collection, location_id).dict()

@app.post("/locations/add")
def add_location(location: Location):
    """
    Adds/Updates a location. Supply address name or lat/long.
    If lat/long already exist, merge the two lists of weeds.
    """
    return LocationService.add(locations_collection, location)

@app.post("/locations/delete")
def delete_location(location: Location):
    """Delete a location"""
    return LocationService.delete(locations_collection, location)

@app.get("/locations/search")
def location_search(point: GeoJSONPoint, max_distance: float):
    """Get locations within max_distance of a point"""
    return LocationService.get_all_with_max_distance(locations_collection, point, max_distance)

@app.post("/weeds/add")
# async def add_weed()
async def add_weed(weed_id: int, discovery_date: str, removed: bool, 
                        removal_date: Optional[str], replaced: bool, replaced_species: Optional[str], 
                        image_filename: Optional[str], file: UploadFile = File(...)):
    """Adds a weed instance"""
    #for some reason can't use 

# async def upload(user: User = Depends(), file: UploadFile = File(...)):

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

@app.post("/files/")
async def create_file(
    fileb: UploadFile = File(...), token: str = Form(...)
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }

# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile = File(...)):
#     print("got" + file.filename)
#     new_name = uuid.uuid4()
#     try:
#         with open(f"files/{new_name}", "wb") as new_file:
#             new_file.write(file.file.read())
#     except:
#         return False
    # return {"filename": file.filename}



@app.get("/species")
def get_species():
    """Get all species"""
    return [x.dict() for x in SpeciesService.get_all(species_db)]

@app.get("/species/")
def get_species_by_id(species_id: int = -1, species_name: str = ""):
    """Get a species by species_id or species_name"""
    if species_id != -1:
        return SpeciesService.get_species_by_id(species_db, species_id).dict()
    elif species_name != "":
        return [x.dict() for x in SpeciesService.get_species_by_name(species_db, species_name)]

    return Response(status_code=status.HTTP_400_BAD_REQUEST)

@app.get("/users", response_model=List[Person])
def get_all_users():
    """Get all users"""
    return UserService.get_all(users_db)


@app.get("/users/", response_model=Person)
def get_user_by_id(person_id: int = None):
    """Get a user by id"""
    if person_id is None:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return UserService.get_person_by_id(users_db, person_id)


@app.post("/users/add", response_model=Person)
def create_user(person: Person):
    """Create a user from Person Model"""
    new_person = UserService.create_person(users_db, person)
    if new_person != person:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/users/delete", response_model=Person)
def delete_user(person_id: int):
    """Delete a user"""
    UserService.delete_person_by_id(users_db, person_id)


@app.post("/users/update", response_model=Person)
def update_user(person_id: int, weed_instance: WeedInstance):
    """Update a user."""
    UserService.update_person_identifications(users_db, person_id, weed_instance)

if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8080, reload=True)
