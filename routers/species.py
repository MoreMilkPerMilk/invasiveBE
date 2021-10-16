from fastapi import APIRouter, Request, HTTPException
from typing import List

import requests

from Models.Species import Species

import routers.photolocations

from db.session import database_instance

router = APIRouter(
    prefix="/species",
    tags=["species"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad input"}
    }
)

@router.get("/", response_model=List[Species])
def get_species(request: Request):
    """Get all species"""
    species_collection = request.app.state.db.data.species

    res = species_collection.find()

    if res is None:
        raise HTTPException(404)

    return [Species(**s) for s in res]

@router.get("/{species_id}", response_model=Species)
def get_species_by_id(request: Request, species_id: int = None):
    """Get a species by species_id"""
    species_collection = request.app.state.db.data.species

    print("got species_id ", species_id)

    res = None

    if species_id is None:
        raise HTTPException(400)

    res = species_collection.find_one({"species_id": int(species_id)})

    return None if res is None else Species(**res)

@router.get("/search/{species_name}", response_model=List[Species])
def species_search(request: Request, species_name: str = ""):
    """Search for a species by species_name"""
    species_collection = request.app.state.db.data.species

    res = None

    if species_name == "" or species_name is None:
        raise HTTPException(400)

    species_collection.drop_indexes()
    species_collection.create_index([("name", "text")])
    res = species_collection.find({ "$text": { "$search": species_name } })

    if res is None:
        raise HTTPException(status_code=404)

    return [Species(**s) for s in res]

@router.put("/populate")
def populate(request: Request):
    print("populating species")
    WEED_URL = "https://weeds.brisbane.qld.gov.au/api/weeds"
    species_collection = request.app.state.db.data.species
    
    r = requests.get(WEED_URL)
    print(r.json())
    entries = []
    for s in r.json():
        entry = {
            "species_id": s["Nid"],
            "name": s["Name"],
            "species": s['Species name'],
            # "info":
            "family": s["Family"],
            "native": True if s["Native/Exotic"] == "Native" else False,  # thx aussie gov't
            "common_names": s["Common names"],
            "notifiable": True if s["Notifiable"] == "Yes" else False,
            "growth_form": s["Growth form"],
            "flower_colour": s["Flower colour"],
            "leaf_arrangement": s["Leaf arrangement"],
            "flowering_time": s["Flowering time"],
            "state_declaration": s["State declaration"],
            "council_declaration": s["Council declaration"],
            "control_methods": s["Control methods"],
            "replacement_species": s["Replacement species"],
        }
        species_collection.insert_one(Species(**entry).dict())