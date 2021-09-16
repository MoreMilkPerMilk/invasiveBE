import json
import pymongo
import logging
import geojson
import shapely.geometry
import shapely.ops

from fastapi import APIRouter, Request, HTTPException
from typing import List
from bson.objectid import ObjectId
from geojson import MultiPolygon
from pymomngo import Collection

from Models.Community import Community 
from Models.Location import Location
from Models.Person import Person
from Models.Event import Event

from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon

import routers

from db.session import database_instance

log = logging.getLogger("backend-logger")

router = APIRouter(
    prefix="/communities",
    tags=["communities"],
    responses={
        404: {"description": "Not found"}}
)

def set_unique_keys(community_collection: Collection):
    """
        Sets community_collection to be uniquely identified by 'name' ASC
    """
    community_collection.create_index(
        [("name", pymongo.ASCENDING)],
        unique=True
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
                "abbreviated_name": 1,
                "area_sqkm": 1,
                "community_events": 1
            }
        }
    ])

    if res is None:
        raise HTTPException(404)

    return [Community(**c) for c in res]

@router.get("/{community_id}", response_model=Community)
def get_community(request: Request, community_id: str):
    """Gets a community by a given id"""
    community_collection = request.app.state.db.data.communities

    res = community_collection.find_one({"_id": community_id})
    
    if res is None: 
        raise HTTPException(404)

    return Community(**res)
    # return [Community(**r) for r in res]

@router.get("/locations", response_model=List[Location])
def get_community_locations(request: Request, community_id: str):
    """Get locations that are within the Community boundary (RETURNS BOUNDARY - MAY SLOW BROWSER)"""
    community = get_community(request, community_id)
    loc = routers.locations.get_all_in_community(request, community)    

    if community is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if loc is None: 
        return []

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

@router.post("/search/location", response_model=List[Community])
def get_community_by_location(request: Request, location: Location):
    """Get a community from a location."""
    community_collection = request.app.state.db.data.communities
    res = community_collection.find({"boundary":{"$geoIntersects":{"$geometry": location.point}}})

    if res is None:
        raise HTTPException(status_code=404, detail="Item not found")

    communities = [Community(**c) for c in res]

    if len(communities) == 0:
        raise HTTPException(status_code=404, detail="Found no communities")
    
    return communities

#############################################
# non council-similar stuff

@router.put("/users/add", response_model=Community)
def add_user_to_community(request: Request, community_id: str, user: Person):
    """Adds a user to a given community"""
    community_collection = request.app.state.db.data.communities
    
    community = get_community(request, community_id)

    if community is None: 
        raise HTTPException(404)

    community_collection.replace_one({"_id": community_id}, community, upsert=True)

    return community

@router.put("/events/add", response_model=Community)
def add_event_to_community(request: Request, community_id: str, event: Event):
    """Adds a event to a given community"""
    community_collection = request.app.state.db.data.communities
    
    community = get_community(request, community_id)

    community.add_event(event)

    if community is None or event is None: 
        raise HTTPException(404)

    if community_collection.replace_one({"_id": community_id}, community.dict(), upsert=True) is None:
        raise HTTPException(404)

    return community

def find_suburb(suburb_name: str) -> dict: 
    """Finds a suburb from suburbs.json"""
    with open("suburbs.json", "r") as geojson_suburbs_f:
        geojson = json.load(geojson_suburbs_f)
    
    if len(geojson) == 0:
        raise HTTPException(400)

    bestRatio = 0
    best = {}

    for feature in geojson['features']:
        # print(feature)
        locality_name = feature['properties']['qld_loca_2']
        
        ratio = fuzz.ratio(locality_name.lower(), suburb_name.lower())
        if ratio > bestRatio:
            bestRatio = ratio 
            best = feature 

    if bestRatio < 45:
        print("best ratio low")
        raise HTTPException(404)
        return {}

    print(f"best ratio {bestRatio}")

    return {"name": best['properties']['qld_loca_2'], "geometry": best['geometry']}

def find_council(council_name: str) -> dict: 
    """Finds a suburb from suburbs.json"""
    with open("mygeodata_merged.json", "r") as geojson_f:
        geojson = json.load(geojson_f)
    
    if len(geojson) == 0:
        raise HTTPException(400)

    bestRatio = 0
    best = {}

    for feature in geojson['features']:
        # print(feature)
        name = feature['properties']['LGA']
        
        ratio = fuzz.ratio(name.lower(), council_name.lower())
        if ratio > bestRatio:
            bestRatio = ratio 
            best = feature 

    if bestRatio < 45:
        print("best ratio low")
        raise HTTPException(404)
        return {}

    print(f"best ratio {bestRatio}")

    return {"name": best['properties']['LGA'], "geometry": best['geometry']}

@router.post("/create", response_model=Community)
def create_community(request: Request, name: str, boundary: dict, suburbs: List = None, councils: List = None):
    """Creates a community"""
    processed_councils = []
    processed_suburbs = []
    if boundary is not None and len(boundary) > 0: 
        #use MultiPolygon
        if 'type' in boundary and boundary['type'] == "MultiPolygon" and 'coordinates' in boundary and len(boundary['coordinates']) > 0:
            boundary_geojson = GeoJSONMultiPolygon(**boundary)
        else:
            log.error("Bad boundary")
            raise HTTPException(404)

    else: 
        boundary = {}
        base = {"type": "MultiPolygon", "coordinates": []}

        base = shapely.geometry.asShape(base)

        if suburbs is not None and len(suburbs) > 0:
            for sub in suburbs:
                suburb = find_suburb(sub)
                if suburb is not {}:
                    suburb_poly = shapely.geometry.asShape(suburb['geometry'])
                    base = base.union(suburb_poly)
                    processed_suburbs.append(suburb['name'].lower().title())

        if councils is not None and len(councils) > 0:
            for co in councils:
                council = find_council(co)
                if council is not {}:
                    council_poly = shapely.geometry.asShape(council['geometry'])
                    base = base.union(council_poly)
                    processed_councils.append(council['name'].lower().title())

        # print(base)
        boundary_geojson = geojson.Feature(geometry=base, properties={})
                
    # print(boundary_geojson)

    communityJson = {"_id": str(ObjectId()), "name": name, "boundary": boundary_geojson['geometry'], "members": [], "events": [], "councils": processed_councils, "suburbs": processed_suburbs}

    community = Community(**communityJson)
    # community._id = ObjectId()

    communities_collection = request.app.state.db.data.communities
    
    res = communities_collection.insert_one(community.dict(by_alias=True))

    if res is None:
        raise HTTPException(404)

    return community