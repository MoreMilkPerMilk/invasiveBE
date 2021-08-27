from fastapi import APIRouter, Request, HTTPException
from typing import List

from Models.Council import Council 
from Models.Location import Location
from Models.GeoJSONPoint import GeoJSONPoint

import routers.councils

from db.session import database_instance

router = APIRouter(
    prefix="/locations",
    tags=["locations"],
    responses={404: {"description": "Not found"}}
)

LOCATIONS = 'locations'

# @router.get("/locations", response_model=List[Location])
@router.get("/", response_model=List[Location])
def get_all_locations(request: Request):
    """
    Return all locations that exist within the collection
    """
    locations_collection = request.state.db[LOCATIONS]
    res = locations_collection.find()

    if res is None:
        raise HTTPException(status_code=404, detail="Could not find")

    return [Location(**i) for i in res] 

@router.get("/{location_id}", response_model=Location)
def get_location_by_id(request: Request, location_id: int = None):
    """Gets a location by id"""
    locations_collection = request.state.db[LOCATIONS]
    if location_id is None:
        raise HTTPException(status_code=404, detail="Didn't get valid location_id")

    res = locations_collection.find_one({"_id": location_id})
    if res is None: 
        raise HTTPException(status_code=404, detail="Could not find")
    
    return Location(**res)

@router.post("/add")
def add_location(request: Request, location: Location):
    """
    Adds/Updates a location. Supply address name or lat/long.
    If lat/long already exist, merge the two lists of weeds.
    """
    return None

@router.post("/locations/delete")
def delete_location(location: Location):
    """Delete a location"""
    return None

@router.get("/locations/search")
def location_search(point: GeoJSONPoint, max_distance: float):
    """Get locations within max_distance of a point"""
    return None
