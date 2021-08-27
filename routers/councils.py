from fastapi import APIRouter, Request, HTTPException
from typing import List

from ..Models.Council import Council 
from ..Models.Location import Location

import locations

from db.session import database_instance

router = APIRouter(
    prefix="/councils",
    tags=["councils"],
    responses={404: {"description": "Not found"}}
)

@router.get("/councils", response_model=List[Council])
def get_councils(request: Request) -> List[Council]:
    """
        Returns all councils in the database
    """
    council_collection = request.app.state.db['councils']
    return [Council(**c) for c in council_collection.find()]

@router.get("/councils/{council_id}", response_model=List[Council])
def get_council(request: Request, council_id: int = None):
    """Gets a council by a given id."""
    council_collection = request.app.state.db['councils']
    res = council_collection.find_one({"_id": id})
    
    return None if res is None else Council(**res)

@router.get("/councils/{abb_name}", response_model=List[Council])
def get_council_by_abbreviated_name(request: Request, abb_name: str = None):
    """Gets a council by it's abbreviated name."""
    council_collection = request.app.state.db['councils']
    q = council_collection.find_one({"abbreviated_name": abb_name})

    if not q.alive() or q is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Council(**q)

@router.get("/councils/{location}", reponse_model=List[Council])
def get_council_by_location(request: Request, location: Location):
    """Get a council from a location."""
    council_collection = request.app.state.db['councils']
    councils = council_collection.find({"boundary":{"$geoIntersects":{"$geometry": location.point}}})

    if councils is None:
        raise HTTPException(status_code=404, detail="Item not found")

    res = [Council(**c) for c in councils]

    if len(res) > 1:
        print("get_council_from_location() - more than one council found?")
        print([Council(**c) for c in councils])
        raise HTTPException(status_code=404, detail="Found many councils")
    
    return res[0]

@router.get("/council/locations", response_model=List[Location])
def get_council_locations(request: Request, council_id: int = None):
    """Get locations that are within the Council boundary"""
    council = get_council(request, council_id)
    loc = locations.get_all_in_council(request, council)    

    if council is None or loc is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return [Location(**l) for l in loc]

