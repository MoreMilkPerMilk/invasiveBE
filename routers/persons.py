from fastapi import APIRouter, Request, HTTPException
from typing import List

from Models.Council import Council 
from Models.Location import Location
from Models.Person import Person
from Models.WeedInstance import WeedInstance

import routers.locations

from db.session import database_instance

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[Person])
def get_all_users(request: Request):
    """Get all users"""
    users_collection = request.app.state.db.data.users

    return [Person(**x) for x in users_collection.find()]


@router.get("/{user_id}", response_model=Person)
def get_user_by_id(request: Request, user_id: int = None):
    """Get a user by id"""
    if user_id is None:
        raise HTTPException(status_code=404, detail="No user_id")
    
    users_collection = request.app.state.db.data.users
    person = users_collection.find_one({"person_id": user_id})

    return None if person is None else Person(**person)


@router.post("/add", response_model=Person)
def create_user(request: Request, person: Person):
    """Create a user from Person Model !!!"""
    users_collection = request.app.state.db.data.users

    #set unique keys so can't insert double ups
    r = users_collection.insert_one(person.dict(by_alias=True))

    if r is None:
        raise HTTPException(status_code=404, detail="Could not add user.")


@router.post("/delete", response_model=Person)
def delete_user(request: Request, person_id: int):
    """Delete a user"""
    users_collection = request.app.state.db.data.users
    users_collection.delete_many({"person_id": person_id})

@router.put("/add_identification", response_model=Person)
def update_user(request: Request, person_id: int, weed_instance: WeedInstance):
    """Adds a WeedInstance to a user"""
    users_collection = request.app.state.db.data.users
    
    key = {"person_id": person_id}
    res = users_collection.find_one(key)

    if res is None:
        raise HTTPException(404)

    person = Person(**res)
    person.add_identification(weed_instance)
    users_collection.replace_one(key, person.dict(), upsert=True)