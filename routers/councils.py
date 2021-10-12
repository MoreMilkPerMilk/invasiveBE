import json
import pymongo
import logging
import shapely

from fastapi import APIRouter, Request, HTTPException
from typing import List
from bson.objectid import ObjectId
from geojson import MultiPolygon
from pymongo.collection import Collection

from Models.Council import Council 
from Models.PhotoLocation import PhotoLocation
from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon

import routers.photolocations as photolocations

from db.session import database_instance

log = logging.getLogger("backend-logger")

router = APIRouter(
    prefix="/councils",
    tags=["councils"],
    responses={404: {"description": "Not found"}}
)

def set_unique_keys(council_collection: Collection):
    """Sets council_collection to be uniquely identified by 'name' ASC"""
    council_collection.create_index(
        [("name", pymongo.ASCENDING)],
        unique=True
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

@router.get("/photolocations", response_model=List[PhotoLocation])
def get_council_photolocations(request: Request, council_id: int):
    """Get photolocations that are within the Council boundary (RETURNS BOUNDARY - MAY SLOW BROWSER)"""
    council = get_council(request, council_id)
    loc = photolocations.get_all_in_council(request, council)    

    if council is None or loc is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return [PhotoLocation(**l) for l in loc]

@router.get("/search", response_model=List[Council])
def search_council_names(request: Request, search_term: str = None):
    """Search for councils by a given search_term"""
    print("h")
    council_collection = request.app.state.db.data.councils

    print("search", search_term)
    #check
    # council_collection.create_index([("name", "text")])
    council_collection.drop_indexes()
    council_collection.create_index([("name", "text")])
    res = council_collection.find({ "$text": { "$search": search_term } })


    # res = council_collection.find({ "$text": { "$search": search_term } })

    if res is None: 
        raise HTTPException(404)

    print(res)

    return [Council(**r) for r in res]

@router.post("/search/polygon", response_model=List[Council])
def get_councils_by_polygon(request: Request, polygon: GeoJSONMultiPolygon, simplify_tolerance: float):
    """Get a council from a polygon. simplify_tolerance specifies the max distance from the true polygon for simplification."""
    council_collection = request.app.state.db.data.councils 

    d = polygon.to_geojson()
    d['type'] = "Polygon"
    
    res = council_collection.find({"boundary":{"$geoIntersects":{"$geometry": d}}})

    # prit

    if res is None:
        raise HTTPException(status_code=404, detail="No items found")

    # councils = [Council(**c) for c in res]
    councils = []
    for c in res:

        g = [x.buffer(0).simplify(simplify_tolerance, preserve_topology=False) for x in shapely.geometry.shape(c['boundary'])]
        coords = [[[float(i[0]), float(i[1])] for i in poly.exterior.coords[:-1]] for poly in g]
        c['boundary']['coordinates'] = coords
        print(c)
        try:
            council = Council(**c)
            councils.append(council)
        except Exception:
            print("exception")

        # print(g)
        # print(coords)
        # return []
        # print("council boundary", council.boundary)
        # geoPolygon = GeoJSONMultiPolygon(**council.boundary)

        # print("coordinates", council.boundary.coordinates)

        # shapely.geometry.Polygon([(a[0], a[1]) for a in council.boundary.coordinates[0]])

        # councils.append()

    if len(councils) == 0:
        raise HTTPException(status_code=404, detail="Found no councils")
    
    return councils

@router.post("/search/location", response_model=List[Council])
def get_council_by_location(request: Request, location: PhotoLocation):
    """Get a council from a location."""
    council_collection = request.app.state.db.data.councils
    res = council_collection.find({"boundary":{"$geoIntersects":{"$geometry": location.point.dict()}}})

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
                        "photolocations": []}

        councilJson['_id'] = str(ObjectId())

        council = Council(**councilJson)

        done += 1

        try:
            council_collection.insert_one(council.dict(by_alias=True)) 
        except Exception as e:
            log.error(e)
            raise HTTPException(status_code=404, detail="failed to add council to collection")
            done -= 1
        


