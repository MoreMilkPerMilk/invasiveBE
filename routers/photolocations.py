import logging
import pymongo
import uuid

from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from typing import List
from pymongo.collection import Collection

from Models.Council import Council 
from Models.PhotoLocation import PhotoLocation
from Models.GeoJSONPoint import GeoJSONPoint
from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon

import routers.councils

from db.session import database_instance

router = APIRouter(
    prefix="/photolocations",
    tags=["photolocations"],
    responses={404: {"description": "Not found"}}
)

log = logging.getLogger("backend-logger")

def set_unique_keys(location_collection: Collection):
    """
        Sets location_collection to be uniquely identified by 'point' ASC
    """
    location_collection.create_index(
        [
            ("point", pymongo.ASCENDING),
            ("image_filename", pymongo.ASCENDING),
        ],
        unique=True
    )

@router.get("/", response_model=List[PhotoLocation])
def get_all_photolocations(request: Request):
    """
    Return all photolocations that exist within the collection
    """
    photolocations_collection = request.app.state.db.data.photolocations
    res = photolocations_collection.find()

    if res is None:
        raise HTTPException(status_code=404, detail="Could not find")

    return [PhotoLocation(**i) for i in res] 

@router.get("/{location_id}", response_model=PhotoLocation)
def get_location_by_id(request: Request, location_id: str = None):
    """Gets a location by id"""
    photolocations_collection = request.app.state.db.data.photolocations
    if location_id is None:
        raise HTTPException(status_code=404, detail="Didn't get valid location_id")

    res = photolocations_collection.find_one({"_id": location_id})
    if res is None: 
        raise HTTPException(status_code=404, detail="Could not find")
    
    return PhotoLocation(**res)

@router.post("/council/", response_model=List[PhotoLocation])
def get_all_in_council(request: Request, council: Council) -> List[PhotoLocation]:
    """Get all photolocations for a council using geojson query."""
    location_collection = request.app.state.db.data.photolocations
    councils_collection = request.app.state.db.data.councils

    if council is None:
        log.error("get_all_inc_council() - Council is None")
        raise HTTPException(404)

    photolocations = location_collection.find({
        "point": {
            "$geoWithin": {
                "$geometry": council.boundary
            }
        }
    })

    if photolocations is None:
        log.error("get_all_inc_council() - PhotoLocations is None")
        raise HTTPException(404)

    return [PhotoLocation(**loc).dict() for loc in photolocations]

@router.post("/add")
def add_location(request: Request, point: GeoJSONMultiPolygon, file: UploadFile = File(...)):
    """
    Adds a Photo-Location pair to the database
    """
    photolocations_collection = request.app.state.db.data.photolocations

    location = PhotoLocation(**{"point": point, "image_filename": ""})

    new_filename = uuid.uuid4()

    try:
        with open(f"files/{new_filename}", "wb") as new_file: 
            new_file.write(file.file.read())

        location.image_filename = new_filename
        photolocations_collection.insert_one(location.dict())

    except Exception as e:
        log.error(f"Failed to add location - {e}")
        raise HTTPException(404)

@router.put("/update")
def update_location(request: Request, location_id: str, location: PhotoLocation):
    """
        Update a PhotoLocation
    """
    photolocations_collection = request.app.state.db.data.photolocations
    
    key = {"_id": location_id}
    res = photolocations_collection.find_one(key)

    if res is None:
        raise HTTPException(404)
        
    photolocations_collection.replace_one(key, location.dict(), upsert=True)

@router.delete("/delete/{location_id}")
def delete_location(request: Request, location_id: str = None):
    """Delete a location"""
    photolocations_collection = request.app.state.db.data.photolocations

    res = photolocations_collection.delete_many({"_id": location_id})

    if res is None:
        raise HTTPException(404)
    
    return True

@router.get("/near", response_model=List[PhotoLocation])
def location_near(request: Request, point: GeoJSONPoint, max_distance: float):
    """Get photolocations within max_distance of a point"""
    photolocations_collection = request.app.state.db.data.photolocations

    if point is None:
        log.error("get_all_in_radius() - point is none")
        raise HTTPException(404)
    
    photolocations = photolocations_collection.find( {
        "point": { "$near": point,  "$maxDistance": max_distance }
    })

    if photolocations is None:
        log.error("get_all_with_max_distace() photolocations is None")
        raise HTTPException(404)
    
    return [PhotoLocation(**loc).dict() for loc in photolocations]

@router.get("/search", response_model=List[PhotoLocation])
def location_search(request: Request, search_term: str):
    """Search for photolocations by a given search_term"""
    photolocations_collection = request.app.state.db.data.photolocations 

    #make sure is indexed
    photolocations_collection.create_index([("name", "text")])
    
    res = photolocations_collection.find({ "$text": { "$search": search_term } })
    
    return [] if res is None else [PhotoLocation(**r) for r in res]
