from fastapi import APIRouter, Request, HTTPException
from typing import List

from Models.Species import Species

import routers.locations

from db.session import database_instance

router = APIRouter(
    prefix="/species",
    tags=["species"],
    responses={404: {"description": "Not found"}}
)

SPECIES = 'species'

@router.get("/", response_model=List[Species])
def get_species(request):
    """Get all species"""
    species_collection = request.state.db.data[SPECIES]

    res = species_collection.find()

    if res is None:
        raise HTTPException(status_code=404)

    return [Species(**s) for s in res]

@router.get("/search")
def get_species_by_id(request: Request, species_id: int = -1, species_name: str = ""):
    """Get a species by species_id or species_name"""
    species_collection = request.app.state.db.data[SPECIES]

    res = None

    if species_id != -1:
        res = species_collection.find_one({"species_id": species_id})
    elif species_name != "":
        res = species_collection.aggregate([
            {
                "$search": {
                "text": {
                    "path": "species_name",
                    "query": species_name,
                    "fuzzy": {}
                }
                }
            }])

    if res is None:
        raise HTTPException(status_code=404)

    return [Species(**s) for s in res]