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
from Models.Person import Person
from Models.WeedInstance import WeedInstance
from Models.Location import Location
from Models.Species import Species
from Models.Council import Council
from Models.GeoJSONPoint import GeoJSONPoint

app = FastAPI()
# client = connect_to_mongodb()
# p = pprint.PrettyPrinter(sort_dicts=False)
p = pprint.PrettyPrinter()
log = logging.getLogger("backend-logger")
loc_db = client['locations2']
species_db = client['species']
weeds_db = client['weed_instances']
users_db = client['users']
council_db = client['councils']

# loc_db.remove()
# loc_db.remove( { } )

# SETUP UNIQUE KEYS
LocationService.set_unique_keys(loc_db)
CouncilService.set_unique_keys(council_db)
WeedInstanceService.set_unique_keys(weeds_db)

# @app.get("/locations", response_model=List[Location])
@app.get("/locations", response_model=List[Location])
def get_all_locations():
    """
    Return all locations that exist within the databases
    """
    return LocationService.get_all(loc_db)

@app.get("/location/", response_model=Location)
def get_location_by_id(location_id: int = None):
    """Gets a location by id"""
    if location_id is None:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    return LocationService.get_by_id(loc_db, location_id).dict()

@app.post("/locations/add")
def add_location(location: Location):
    """
    Adds/Updates a location. Supply address name or lat/long.
    If lat/long already exist, merge the two lists of weeds.
    """
    return LocationService.add(loc_db, location)

@app.post("/locations/delete")
def delete_location(location: Location):
    """Delete a location"""
    return LocationService.delete(loc_db, location)

@app.get("/locations/search")
def location_search(point: GeoJSONPoint, max_distance: float):
    """Get locations within max_distance of a point"""
    return LocationService.get_all_with_max_distance(loc_db, point, max_distance)

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

    return WeedInstanceService.add_weed(weeds_db, weed, file)

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

@app.get("/councils", response_model=List[Council])
def get_councils():
    """
        Returns all councils in the database
    """
    return get_councils()

@app.get("/councils/", response_model=List[Council])
def get_council(council_id: int = None):
    """Gets a council by a given id."""
    return CouncilService.get_council_by_id(council_id) 

@app.get("/council/locations", response_model=List[Location])
def get_council_locations(council_id: int = None):
    """Get locations that are within the Council boundary"""
    council = CouncilService.get_council_by_id(council_id)
    loc = LocationService.get_all_in_council(loc_db, council)    

    if council is None or loc is None:
        log.error(f"Council or loc is None")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

# g = CouncilService.get_council_from_location(council_db, Location(**{"name": "St Lucia", "weeds_present": [], "point": Point((153.000042,-27.499159))}))

@app.get("/hamish")
def hamish():
    """Flutter"""
    return "Flutter"


if __name__ == '__main__':
    uvicorn.run("BackendController:app", host='0.0.0.0', port=80, reload=True)
