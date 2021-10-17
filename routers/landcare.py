import json
import pymongo
import logging
import shapely
import numpy as np

from fastapi import APIRouter, Request, HTTPException
from typing import List
from bson.objectid import ObjectId
from geojson import MultiPolygon
from pymongo.collection import Collection

from Models.Landcare import Landcare 
from Models.PhotoLocation import PhotoLocation
from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon

import routers.photolocations as photolocations

from db.session import database_instance

log = logging.getLogger("backend-logger")

router = APIRouter(
    prefix="/landcares",
    tags=["landcares"],
    responses={404: {"description": "Not found"}}
)

def set_unique_keys(landcare_collection: Collection):
    """Sets landcare_collection to be uniquely identified by 'name' ASC"""
    landcare_collection.create_index(
        [("name", pymongo.ASCENDING)],
        unique=True
    )

@router.get("/peek", response_model=List[Landcare])
def peek_landcares(request: Request) -> List[Landcare]:
    """
        Returns landcares in the database (w/o polygon boundary as too large, request single landcare for boundary).
    """
    landcare_collection = request.app.state.db.data.landcares

    res = landcare_collection.aggregate([
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

    return [Landcare(**c) for c in res]

@router.get("/{landcare_id}", response_model=List[Landcare])
def get_landcare(request: Request, landcare_id: str):
    """Gets a landcare by a given id"""
    landcare_collection = request.app.state.db.data.landcares

    res = landcare_collection.find({"_id": landcare_id})
    
    if res is None: 
        raise HTTPException(404)

    return [Landcare(**r) for r in res]

@router.post("/search/polygon", response_model=List[Landcare])
def get_landcares_by_polygon(request: Request, polygon: GeoJSONMultiPolygon, simplify_tolerance: float):
    """Get a landcare from a polygon. simplify_tolerance specifies the max distance from the true polygon for simplification."""
    landcare_collection = request.app.state.db.data.landcares 

    d = polygon.to_geojson()
    d['type'] = "Polygon"
    
    res = landcare_collection.find({"boundary":{"$geoIntersects":{"$geometry": d}}})

    # prit

    if res is None:
        raise HTTPException(status_code=404, detail="No items found")

    landcares = []
    
    for c in res:
        try:
            g = [x.buffer(0).simplify(simplify_tolerance, preserve_topology=False) for x in shapely.geometry.shape(c['boundary'])]
        except Exception: 
            print("couldn't load boundary, probably fine :)")
            continue

        coords = []
        for poly in g:
            if isinstance(poly, shapely.geometry.MultiPolygon):
                for poly2 in poly:
                    coords.append([[float(i[0]), float(i[1])] for i in poly2.exterior.coords[:-1]])
            else:
                coords.append([[float(i[0]), float(i[1])] for i in poly.exterior.coords[:-1]])

        c['boundary']['coordinates'] = coords

        try:
            landcare = Landcare(**c)
            landcares.append(landcare)
        except Exception:
            print("Exception appending landcare.")

    if len(landcares) == 0:
        raise HTTPException(status_code=404, detail="Found no landcares")
    
    return landcares

@router.post("/setup")
def create_landcare_collections_from_geojson(request: Request, geojson_filename: str):
    """Adds Landcares from geojson file converted from data.gov"""
    with open(geojson_filename, "r") as geojson_f:
        geojson = json.load(geojson_f)

    if len(geojson) == 0:
        # raise Exception(f"Could not open geojson file {geojson_filename}"
        raise HTTPException(400, detail=f"Could not open geojson file {geojson_filename}")

    landcare_collection = request.app.state.db.data.landcares

    expected = len(geojson['features'])
    done = 0

    for feature in geojson['features']:
        prop = feature['properties']
        print(f"Adding {prop['STATE']} {prop['AREA_DESC']} to Landcares")
        my_polygon = MultiPolygon(feature['geometry']['coordinates'])

        landcareJson = {"state": prop['STATE'], 
                        "area_desc": prop['AREA_DESC'],
                        "nrm_id": int(prop['NRM_ID']),
                        "boundary": MultiPolygon(feature['geometry']['coordinates']), 
                        "nlp_mu": prop['NLP_MU'], #unnecessary
                        "shape_area": float(prop['SHAPE_AREA']),
                        "shape_len": float(prop['SHAPE_LEN'])}

        landcareJson['_id'] = str(ObjectId())

        landcare = Landcare(**landcareJson)

        done += 1

        try:
            landcare_collection.insert_one(landcare.dict(by_alias=True)) 
        except Exception as e:
            log.error(e)
            raise HTTPException(status_code=404, detail="failed to add landcare to collection")
            done -= 1
        


