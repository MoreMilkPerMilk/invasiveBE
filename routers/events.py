import pymongo

# from typing_extensions import ParamSpecKwargs
from fastapi import APIRouter, Request, HTTPException
from typing import List
from bson.objectid import ObjectId
from pymongo.collection import Collection

from Models.Event import Event

import routers.photolocations as photolocations

from db.session import database_instance

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "bad input"}
    }
)

def set_unique_keys(event_collection: Collection):
    """
        Sets event_collection to be uniquely identified by 'name' ASC
    """
    event_collection.create_index(
        [("name", pymongo.ASCENDING)],
        unique=True
    )

@router.get("/", response_model=List[Event])
def get_events(request: Request) -> List[Event]:
    """
        Returns all events in collection
    """
    events_collection = request.app.state.db.data.events 

    res = events_collection.find()

    if res is None:
        raise HTTPException(404)

    return [Event(**t) for t in res]

@router.get("/{_id}", response_model=Event)
def get_event_by_id(request: Request, _id: str = None):
    """
        Get event by id
    """
    events_collection = request.app.state.db.data.events 

    res = events_collection.find_one({"_id": ObjectId(_id)})
    # print(res)

    if res is None: 
        raise HTTPException(404)

    return Event(**res) #?

@router.post("/add")
def add_event(request: Request, event: Event = None):
    """
        Add event to collection    
    """
    events_collection = request.app.state.db.data.events 

    res = events_collection.insert_one(event.dict(by_alias=True))

    if res is None: 
        raise HTTPException(404)

    # return {"inserted_id": res.inserted_id}
    event._id = res.inserted_id
    return event

@router.delete("/delete")
def delete_event(request: Request, event_id: str = None):
    """
        Deletes a event in collection by it's ObjectId()
    """
    events_collection = request.app.state.db.data.events 
    res = events_collection.delete_many({"_id": ObjectId(event_id)})

    if res is None:
        raise HTTPException(400)

    if res.deleted_count == 0:
        raise HTTPException(404)