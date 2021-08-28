from fastapi import APIRouter, Request, HTTPException
from typing import List
from bson.objectid import ObjectId

import pymongo

from Models.Council import Council 
from Models.Location import Location

import routers.locations as locations

from db.session import database_instance

router = APIRouter(
    prefix="/councils",
    tags=["councils"],
    responses={404: {"description": "Not found"}}
)

@router.get("/all", response_model=List[Council])
def get_councils(request: Request) -> List[Council]:
    """
        Returns all councils in the database (MAX 5)
        (VERRRY SLOW) -> don't use
    """
    council_collection = request.app.state.db.data.councils

    res =  council_collection.find(limit=5) # five limit

    if res is None:
        raise HTTPException(status_code=404)

    return [Council(**c) for c in res]

@router.get("/{council_id}", response_model=List[Council])
def get_council(request: Request, council_id: str = None, search_term: str = None):
    """Gets a council by a given id"""
    council_collection = request.app.state.db.data.councils

    #check
    council_collection.create_index([("name", "text")])

    if council_id is not None:
        res = council_collection.find({"_id": ObjectId(council_id)})
    elif search_term is not None: 
        # res = council_collection.aggregate([
            # {
                # "$search": {
                # "text": {
                    # "path": ["abbreviated_name", "name"],
                    # "query": search_term,
                    # "fuzzy": {}
                # }
                # }
            # }])
        res = council_collection.find({ "$text": { "$search": search_term } })

    if res is None: 
        raise HTTPException(404)

    return [Council(**r) for r in res]

@router.get("/locations", response_model=List[Location])
def get_council_locations(request: Request, council_id: int):
    """Get locations that are within the Council boundary"""
    council = get_council(request, council_id)
    loc = locations.get_all_in_council(request, council)    

    if council is None or loc is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return [Location(**l) for l in loc]

@router.get("/search", response_model=List[Council])
def search_council_names(request: Request, search_term: str = None):
    """Search for councils by a given search_term"""
    council_collection = request.app.state.db.data.councils

    #check
    council_collection.create_index([("name", "text")])

    res = council_collection.find({ "$text": { "$search": search_term } })

    if res is None: 
        raise HTTPException(404)

    return [Council(**r) for r in res]

@router.get("/search/location", response_model=List[Council])
def get_council_by_location(request: Request, location: Location):
    """Get a council from a location."""
    council_collection = request.app.state.db.councils
    res = council_collection.find({"boundary":{"$geoIntersects":{"$geometry": location.point}}})

    if res is None:
        raise HTTPException(status_code=404, detail="Item not found")

    councils = [Council(**c) for c in res]

    if len(councils) == 0:
        raise HTTPException(status_code=404, detail="Found no councils")
    
    return councils



