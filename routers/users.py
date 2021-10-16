import pymongo
import time

from fastapi import APIRouter, Request, HTTPException
from typing import List
from pymongo.collection import Collection
import numpy as np
from bson.objectid import ObjectId


from Models.Council import Council 
from Models.PhotoLocation import PhotoLocation
from Models.User import User
from Models.Report import Report

import routers.photolocations

from db.session import database_instance

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

def set_unique_keys(location_collection: Collection):
    """
        Sets users_collection to be uniquely identified by compound 'first_name', 'last_name', '_id', 'mac_address' ASC
    """
    location_collection.create_index([
        ("_id", pymongo.ASCENDING),
        ("first_name", pymongo.ASCENDING),
        ("last_name", pymongo.ASCENDING),
        ("mac_address", pymongo.ASCENDING)
    ],
        unique=True
    )

@router.get("/", response_model=List[User])
def get_all_users(request: Request):
    """Get all users"""
    users_collection = request.app.state.db.data.users

    return [User(**x) for x in users_collection.find()]

@router.get("/{user_id}", response_model=User)
def get_user_by_id(request: Request, user_id: str = None):
    """Get a user by id"""
    if user_id is None:
        raise HTTPException(status_code=404, detail="No user_id")
    
    users_collection = request.app.state.db.data.users
    user = users_collection.find_one({"_id": user_id})

    return None if user is None else User(**user)

@router.get("/mac/{mac_address}", response_model=User)
def get_user_by_mac_address(request: Request, mac_address: str = None):
    """Get a user by mac address"""
    if mac_address is None: 
        raise HTTPException(status_code=404, detail="No mac_address")
    
    users_collection = request.app.state.db.data.users
    user = users_collection.find_one({"mac_address": mac_address})

    return None if user is None else User(**user)

@router.post("/createbymacaddress/{mac_address}", response_model=User)
def create_user_by_mac_address(request: Request, mac_address: str = None):
    """Create a user by mac address. If already exists, will return."""
    users_collection = request.app.state.db.data.users

    if mac_address is None:
        return HTTPException(400, "No mac address")

    first_names = ["Jane", "John", "James", "Mary"]
    last_names = ["Smith", "Doe"]

    user = User(**{
                '_id': str(ObjectId()),
                'first_name': str(np.random.choice(first_names)), 
                'last_name': str(np.random.choice(last_names)),
                'date_joined': int(time.time()), 
                'reports': [], 
                'mac_address': mac_address,
                'added_details': False})

    try:
        r = users_collection.insert_one(user.dict(by_alias=True))
    except Exception as e:
        return get_user_by_mac_address(request, mac_address)
        # print("There was an exception")
        # raise HTTPException(status_code=401, detail="Exception inserting user, probably was a duplicate.")

    d = user.dict(by_alias=True) 
    d['_id'] = r.inserted_id 

    return d

@router.post("/create", response_model=User)
def create_user(request: Request, user: User):
    """Create a user from User Model !!! PLZ CREATE FROM MAC ADDRESS THEN UPDATE THANKS, OR SUPPLY MAC ADDRESS"""
    users_collection = request.app.state.db.data.users

    user.date_joined = int(time.time())
    user.mac_address = request.g

    #set unique keys so can't insert double ups
    try:
        r = users_collection.insert_one(user.dict(by_alias=True))
    except Exception as e:
        print("There was an exception")
        raise HTTPException(status_code=401, detail="Exception inserting user, probably was a duplicate.")

    if r is None:
        raise HTTPException(status_code=404, detail="Could not add user.")

    d = user.dict(by_alias=True)
    d['_id'] = r.inserted_id

    return d


@router.delete("/delete", response_model=User)
def delete_user(request: Request, user_id: str):
    """Delete a user"""
    users_collection = request.app.state.db.data.users
    users_collection.delete_many({"_id": user_id})

@router.put("/add_report", response_model=User)
def add_report(request: Request, user_id: str, report: Report):
    """Adds a Report to a user"""
    users_collection = request.app.state.db.data.users
    
    key = {"_id": user_id}
    res = users_collection.find_one(key)

    if res is None:
        raise HTTPException(404)

    user = User(**res)
    user.add_report(report)
    users_collection.replace_one(key, user.dict(by_alias=True), upsert=True)

    return user

@router.put("/addreportbyid", response_model=User)
def add_report_by_id(request: Request, user_id: str, report_id: str):
    """Adds a Report to a user"""
    users_collection = request.app.state.db.data.users
    reports_collection = request.app.state.db.data.reports
    
    key = {"_id": user_id}
    res = users_collection.find_one(key)
    report_key = {"_id": report_id}
    report_res = reports_collection.find_one(report_key)

    if res is None:
        raise HTTPException(404, "User not found")

    user = User(**res)

    if report_res is None:
        raise HTTPException(404, "Report not found")

    report = Report(**report_res)
    user.add_report(report)
    users_collection.replace_one(key, user.dict(by_alias=True), upsert=True)

    return user.dict(by_alias=True)

@router.put("/update", response_model=User)
def add_report_by_id(request: Request, user: User):
    """Adds a Report to a user"""
    users_collection = request.app.state.db.data.users
    
    key = {"_id": user._id}
    res = users_collection.find_one(key)

    if res is None:
        raise HTTPException(404, "User not found")

    users_collection.replace_one(key, user.dict(by_alias=True), upsert=True)

    return user.dict(by_alias=True)