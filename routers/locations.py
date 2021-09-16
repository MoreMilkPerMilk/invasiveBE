import logging
import pymongo

from fastapi import APIRouter, Request, HTTPException
from typing import List
from pymongo.collection import Collection

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

log = logging.getLogger("backend-logger")

def set_unique_keys(location_collection: Collection):
    """
        Sets location_collection to be uniquely identified by 'point' ASC
    """
    location_collection.create_index(
        [("point", pymongo.ASCENDING)],
        unique=True
    )

# @router.get("/locations", response_model=List[Location])
@router.get("/", response_model=List[Location])
def get_all_locations(request: Request):
    """
    Return all locations that exist within the collection
    """
    locations_collection = request.app.state.db.data.locations
    res = locations_collection.find()

    if res is None:
        raise HTTPException(status_code=404, detail="Could not find")

    return [Location(**i) for i in res] 

@router.get("/{location_id}", response_model=Location)
def get_location_by_id(request: Request, location_id: int = None):
    """Gets a location by id"""
    locations_collection = request.app.state.db.data.locations
    if location_id is None:
        raise HTTPException(status_code=404, detail="Didn't get valid location_id")

    res = locations_collection.find_one({"_id": location_id})
    if res is None: 
        raise HTTPException(status_code=404, detail="Could not find")
    
    return Location(**res)

@router.post("/council/", response_model=List[Location])
def get_all_in_council(request: Request, council: Council) -> List[Location]:
    """Get all locations for a council using geojson query."""
    location_collection = request.app.state.db.data.locations
    councils_collection = request.app.state.db.data.councils

    if council is None:
        log.error("get_all_inc_council() - Council is None")
        raise HTTPException(404)

    locations = location_collection.find({
        "point": {
            "$geoWithin": {
                "$geometry": council.boundary
            }
        }
    })

    if locations is None:
        log.error("get_all_inc_council() - Locations is None")
        raise HTTPException(404)

    return [Location(**loc).dict() for loc in locations]

@router.post("/add")
def add_location(request: Request, location: Location):
    """
    Adds/Updates a location. Supply address name or lat/long.
    If lat/long already exist, merge the two lists of weeds.
    """
    locations_collection = request.app.state.db.data.locations

    res = locations_collection.insert_one(location.dict(by_alias=True))

    if res is None:
        raise HTTPException(404)
    
    return True

@router.delete("/delete")
def delete_location(request: Request, location: Location):
    """Delete a location"""
    locations_collection = request.app.state.db.data.locations

    res = locations_collection.insert_one(location)

    if res is None:
        raise HTTPException(404)
    
    return True

@router.get("/near", response_model=List[Location])
def location_near(request: Request, point: GeoJSONPoint, max_distance: float):
    """Get locations within max_distance of a point"""
    locations_collection = request.app.state.db.data.locations

    if point is None:
        log.error("get_all_in_radius() - point is none")
        raise HTTPException(404)
    
    locations = locations_collection.find( {
        "point": { "$near": point,  "$maxDistance": max_distance }
    })

    if locations is None:
        log.error("get_all_with_max_distace() locations is None")
        raise HTTPException(404)
    
    return [Location(**loc).dict() for loc in locations]

@router.get("/search", response_model=List[Location])
def location_search(request: Request, search_term: str):
    """Search for locations by a given search_term"""
    locations_collection = request.app.state.db.data.locations 

    #make sure is indexed
    locations_collection.create_index([("name", "text")])
    
    res = locations_collection.find({ "$text": { "$search": search_term } })
    
    return [] if res is None else [Location(**r) for r in res]
