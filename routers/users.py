import pymongo

from fastapi import APIRouter, Request, HTTPException
from typing import List
from pymongo.collection import Collection

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
        Sets users_collection to be uniquely identified by compound 'first_name', 'last_name', '_id' ASC
    """
    location_collection.create_index([
        ("_id", pymongo.ASCENDING),
        ("first_name", pymongo.ASCENDING),
        ("last_name", pymongo.ASCENDING)
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

@router.post("/create", response_model=User)
def create_user(request: Request, user: User):
    """Create a user from User Model !!!"""
    users_collection = request.app.state.db.data.users

    #set unique keys so can't insert double ups
    r = users_collection.insert_one(user.dict(by_alias=True))

    if r is None:
        raise HTTPException(status_code=404, detail="Could not add user.")


@router.delete("/delete", response_model=User)
def delete_user(request: Request, user_id: str):
    """Delete a user"""
    users_collection = request.app.state.db.data.users
    users_collection.delete_many({"_id": user_id})

@router.put("/add_report", response_model=User)
def update_user(request: Request, user_id: str, report: Report):
    """Adds a Report to a user"""
    users_collection = request.app.state.db.data.users
    
    key = {"_id": user_id}
    res = users_collection.find_one(key)

    if res is None:
        raise HTTPException(404)

    user = User(**res)
    user.add_report(report)
    users_collection.replace_one(key, user.dict(), upsert=True)