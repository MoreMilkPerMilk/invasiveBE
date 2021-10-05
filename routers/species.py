from fastapi import APIRouter, Request, HTTPException
from typing import List

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

    species_collection.create_index([("species_name", "text")])
    res = species_collection.find({ "$text": { "$search": species_name } })

    if res is None:
        raise HTTPException(status_code=404)

    return [Species(**s) for s in res]