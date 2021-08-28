import json
import pymongo
import logging

from fastapi import APIRouter, Request, HTTPException
from typing import List
from bson.objectid import ObjectId
from geojson import MultiPolygon

from Models.Council import Council 
from Models.Location import Location

import routers.locations as locations

from db.session import database_instance

log = logging.getLogger("backend-logger")

router = APIRouter(
    prefix="/councils",
    tags=["councils"],
    responses={404: {"description": "Not found"}}
)

@router.get("/peek", response_model=List[Council])
def peek_councils(request: Request) -> List[Council]:
    """
        Returns councils in the database (w/o polygon boundary as too large, request single council for boundary).
    """
    council_collection = request.app.state.db.data.councils

    res = council_collection.aggregate([
        {
            "$limit": 10
        },
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "species_occuring": 1,
                "lga_code": 1,
                "abbreviated_name": 1,
                "area_sqkm": 1
            }
        }
    ])

    if res is None:
        raise HTTPException(404)

    return [Council(**c) for c in res]

@router.get("/{council_id}", response_model=List[Council])
def get_council(request: Request, council_id: str):
    """Gets a council by a given id"""
    council_collection = request.app.state.db.data.councils

    res = council_collection.find({"_id": council_id})
    
    if res is None: 
        raise HTTPException(404)

    return [Council(**r) for r in res]

@router.get("/locations", response_model=List[Location])
def get_council_locations(request: Request, council_id: int):
    """Get locations that are within the Council boundary (RETURNS BOUNDARY - MAY SLOW BROWSER)"""
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

@router.post("/search/location", response_model=List[Council])
def get_council_by_location(request: Request, location: Location):
    """Get a council from a location."""
    council_collection = request.app.state.db.data.councils
    res = council_collection.find({"boundary":{"$geoIntersects":{"$geometry": location.point}}})

    if res is None:
        raise HTTPException(status_code=404, detail="Item not found")

    councils = [Council(**c) for c in res]

    if len(councils) == 0:
        raise HTTPException(status_code=404, detail="Found no councils")
    
    return councils

@router.post("/setup")
def create_council_collections_from_geojson(request: Request, geojson_filename: str):
    """Adds Councils from geojson file converted from data.gov"""
    with open(geojson_filename, "r") as geojson_f:
        geojson = json.load(geojson_f)

    if len(geojson) == 0:
        # raise Exception(f"Could not open geojson file {geojson_filename}"
        raise HTTPException(400, detail=f"Could not open geojson file {geojson_filename}")

    council_collection = request.app.state.db.data.councils

    expected = len(geojson['features'])
    done = 0

    for feature in geojson['features']:
        prop = feature['properties']
        print(f"Adding {prop['LGA']} to Councils")
        my_polygon = MultiPolygon(feature['geometry']['coordinates'])
        councilJson = {"name": prop['LGA'], 
                        "lga_code": int(prop['LGA_CODE']), 
                        "abbreviated_name": prop['ABBREV_NAME'],
                        "area_sqkm": float(prop['CA_AREA_SQKM']),
                        "boundary": MultiPolygon(feature['geometry']['coordinates']), #unnecessary
                        "species_occuring": [],
                        "locations": []}

        councilJson['_id'] = str(ObjectId())

        council = Council(**councilJson)

        done += 1

        try:
            council_collection.insert_one(council.dict(by_alias=True)) 
        except Exception as e:
            log.error(e)
            raise HTTPException(status_code=404, detail="failed to add council to collection")
            done -= 1
        


