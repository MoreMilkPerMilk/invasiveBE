from fastapi import APIRouter, Request, HTTPException
from typing import List
from bson.objectid import ObjectId

import pymongo

from Models.Community import Community 
from Models.Location import Location

import routers.locations as locations

from db.session import database_instance

router = APIRouter(
    prefix="/communities",
    tags=["communities"],
    responses={404: {"description": "Not found"}}
)

@router.get("/peek", response_model=List[Community])
def peek_communities(request: Request) -> List[Community]:
    """
        Returns communities in the database (w/o polygon boundary as too large, request single community for boundary).
    """
    community_collection = request.app.state.db.data.communities

    res = community_collection.aggregate([
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

    return [Community(**c) for c in res]

@router.get("/{community_id}", response_model=List[Community])
def get_community(request: Request, community_id: str = None, search_term: str = None):
    """Gets a community by a given id"""
    community_collection = request.app.state.db.data.communities

    #check
    community_collection.create_index([("name", "text")])

    if community_id is not None:
        res = community_collection.find({"_id": ObjectId(community_id)})
    elif search_term is not None: 
        # res = community_collection.aggregate([
            # {
                # "$search": {
                # "text": {
                    # "path": ["abbreviated_name", "name"],
                    # "query": search_term,
                    # "fuzzy": {}
                # }
                # }
            # }])
        res = community_collection.find({ "$text": { "$search": search_term } })

    if res is None: 
        raise HTTPException(404)

    return [Community(**r) for r in res]

@router.get("/locations", response_model=List[Location])
def get_community_locations(request: Request, community_id: int):
    """Get locations that are within the Community boundary"""
    community = get_community(request, community_id)
    loc = locations.get_all_in_community(request, community)    

    if community is None or loc is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return [Location(**l) for l in loc]

@router.get("/search", response_model=List[Community])
def search_community_names(request: Request, search_term: str = None):
    """Search for communities by a given search_term"""
    community_collection = request.app.state.db.data.communities

    #check
    community_collection.create_index([("name", "text")])

    res = community_collection.find({ "$text": { "$search": search_term } })

    if res is None: 
        raise HTTPException(404)

    return [Community(**r) for r in res]

@router.get("/search/location", response_model=List[Community])
def get_community_by_location(request: Request, location: Location):
    """Get a community from a location."""
    community_collection = request.app.state.db.communities
    res = community_collection.find({"boundary":{"$geoIntersects":{"$geometry": location.point}}})

    if res is None:
        raise HTTPException(status_code=404, detail="Item not found")

    communities = [Community(**c) for c in res]

    if len(communities) == 0:
        raise HTTPException(status_code=404, detail="Found no communities")
    
    return communities



