import logging
import pprint
from typing import *

import uvicorn
from fastapi import FastAPI, Response, status

import LocationService
import SpeciesService
import UserService
from DatabaseService import *
from Models.User import Person
from Models.WeedInstance import WeedInstance
from SpeciesService import *
from Models.Location import Location
from Models.Species import Species

app = FastAPI()
client = connect_to_mongodb()
p = pprint.PrettyPrinter(sort_dicts=False)
log = logging.getLogger("location-logger")
loc_db = client['locations']
species_db = client['species']
weeds_db = client['weed_instances']
users_db = client['users']


# @app.get("/locations", response_model=List[Location])
@app.get("/locations", response_model=List[Location])
def get_all_locations():
    """
    Return all locations that exist within the databases
    """
    return LocationService.get_all(loc_db)


@app.post("/locations/add")
def add_location(location: Location):
    """
    Adds/Updates a location. Supply address name or lat/long.
    If lat/long already exist, merge the two lists of weeds.
    """
    return LocationService.add(loc_db, location)


@app.post("/locations/delete")
def delete_location(location: Location):
    return LocationService.delete(loc_db, location)


@app.get("/species")
def get_species():
    return [x.dict() for x in SpeciesService.get_all(species_db)]


@app.get("/species/")
def get_species_by_id(species_id: int = -1, species_name: str = ""):
    if species_id != -1:
        return SpeciesService.get_species_by_id(species_db, species_id).dict()
    elif species_name != "":
        return [x.dict() for x in SpeciesService.get_species_by_name(species_db, species_name)]

    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/users", response_model=List[Person])
def get_all_users():
    return UserService.get_all(users_db)


@app.get("/users/", response_model=Person)
def get_user_by_id(person_id: int = None):
    if person_id is None:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return UserService.get_person_by_id(users_db, person_id)


@app.post("/users/add", response_model=Person)
def create_user(person: Person):
    new_person = UserService.create_person(users_db, person)
    if new_person != person:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/users/delete", response_model=Person)
def delete_user(person_id: int):
    UserService.delete_person_by_id(users_db, person_id)


@app.post("/users/update", response_model=Person)
def update_user(person_id: int, weed_instance: WeedInstance):
    UserService.update_person_identifications(users_db, person_id, weed_instance)


if __name__ == '__main__':
    uvicorn.run("BackendController:app", host='0.0.0.0', port=8000, reload=True)
