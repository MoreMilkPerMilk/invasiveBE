import logging
import pymongo
import uuid

from fastapi import APIRouter, Request, HTTPException, File, UploadFile, Form
from typing import List
from pymongo.collection import Collection
from bson.objectid import ObjectId

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

@router.get("photobaseurl/", response_model=dict)
def get_photo_url(request: Request):
    """
        prepend to image_filename to get image url. 
    """
    return ["http://invasivesys.uqcloud.net/files/"]

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

@router.post("/create", response_model=PhotoLocation)
def add_location(request: Request, photolocation: PhotoLocation = None):
    """
    Creates a Photo-Location, (REMEMBER to use /uploadphoto)
    Returns the id of the created photolocation
    """
    print("got", photolocation)
    print("hello")
    photolocations_collection = request.app.state.db.data.photolocations

    print(photolocation.dict())

    print("to insert", photolocation.dict())

    try:
        res = photolocations_collection.insert_one(photolocation.dict(by_alias=True)) 
    except pymongo.errors.DuplicateKeyError as e:
        raise HTTPException(404, "Duplicate key error")

    if res is None: 
        raise HTTPException(404)

    d = photolocation.dict(by_alias=True)
    d['_id'] = res.inserted_id

    return d

@router.post("/uploadphoto/{photolocation_id}")
def upload_photo(request: Request, photolocation_id: str, file: UploadFile = File(...)):
    """
    Adds a Photo-Location pair to the database
    """
    photolocations_collection = request.app.state.db.data.photolocations

    key = {"_id": photolocation_id}
    res = photolocations_collection.find_one(key)

    print(key)

    if res is None:
        raise HTTPException(404)

    print(res)
    location = PhotoLocation(**res)
    print(location)


    new_filename = str(uuid.uuid4()) + "." + file.filename.split(".")[-1]
    print("new filename", new_filename, "old", file.filename)

    try:
        with open(f"files/{new_filename}", "wb") as new_file: 
            new_file.write(file.file.read())

        location.image_filename = new_filename
        print("location = ", location.dict())
        res2 = photolocations_collection.replace_one(key, location.dict(by_alias=True), upsert=True)

    except Exception as e:
        log.error(f"Failed to add location - {e}")
        raise HTTPException(404)
    
    d = location.dict()
    
    return d

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
        
    photolocations_collection.replace_one(key, location.dict(by_alias=True), upsert=True)

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

@router.get("/filesearch", response_model=List[PhotoLocation])
def file_search(request: Request, search_term: str):
    """Search for photolocations by a given search_term"""
    photolocations_collection = request.app.state.db.data.photolocations 

    #make sure is indexed
    photolocations_collection.create_index([("image_filename", "text")])
    
    res = photolocations_collection.find({ "$text": { "$search": search_term } })
    
    return [] if res is None else [PhotoLocation(**r) for r in res]
