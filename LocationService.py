import pprint
import logging
import pymongo

from fastapi import Response, status
from geopy.geocoders import Nominatim
from geojson import Point
from pymongo.collection import Collection
from typing import List, Optional, Tuple

from Models.WeedInstance import WeedInstance
from Models.Location import Location
from Models.Council import Council

log = logging.getLogger("location-logger")
# p = pprint.PrettyPrinter(sort_dicts=False)

def set_unique_keys(location_collection: Collection):
    location_collection.create_index(
        [("point", pymongo.ASCENDING)],
        unique=True
    )

def add_test_loc(location_collection: Collection) -> bool:
    """Add 'St Lucia to location_collection"""
    point = Point((153.000042, -27.499159))
    pointJson = {"name": "St Lucia", "point": point, "weeds_present": []}

    try:
        location_collection.insert_one(Location(**pointJson).dict())
    except Exception as e:
        log.error(f"Failed to add test point - {e}")
        return False

    return True

def add_loc(location_collection: Collection, location: Location):
    """Add lcoation to location_collection"""
    try:
        location_collection.insert_one(location.dict())
    except Exception as e:
        log.error(f"Exception thrown during add_loc() - {e}")
        return False
    
    return True

def get_all(loc_db: Collection):
    """Get all Locations"""
    result = list()
    for item in loc_db.find():
        try:
            result.append(Location(**item))
        except:
            result.append(item)
    return [x.dict() for x in result]

def get_all_in_council(location_collection: Collection, council: Council) -> List[Location]:
    """Get all locations for a council using geojson query."""
    if council is None:
        log.error("get_all_inc_council() - Council is None")
        return [] 

    locations = location_collection.find({
        "point": {
            "$geoWithin": {
                "$geometry": council.boundary
            }
        }
    })

    if locations is None:
        log.error("get_all_inc_council() - Locations is None")
        return []

    return [Location(**loc).dict() for loc in locations]

def get_all_with_max_distance(location_collection: Collection, point: Point, max_distance: float):
    if point is None:
        log.error("get_all_in_radius() - point is none")
        return []
    
    locations = location_collection.find( {
        "point": { "$near": point,  "$maxDistance": max_distance }
    })

    if locations is None:
        log.error("get_all_with_max_distace() locations is None")
        return []
    
    return [Location(**loc).dict() for loc in locations]

def get_by_id(location_collectioon: Collection, id: int = None) -> Optional[Location]:
    """Gets a Location by id"""
    res = location_collectioon.find_one({"_id": id})
    
    if res is None:
        return None
    
    return Location(**res)

def get_lat_long_from_address(address: str) -> Tuple[float, float]:
    """Helper for getting lat,long from an address string"""
    geolocator = Nominatim(user_agent="invasiveML")
    loc = geolocator.geocode(address)
    lat, long = None, None
    try:
        lat, long = loc.latitude, loc.longitude
    except AttributeError:
        log.error(f"Latitude and Longitude couldn't be found for addr:{address}")
    return lat, long


# def add(loc_db: Collection, location: Location):
#     if location.point is None:
#         lat, long = get_lat_long_from_address(location.name)
#         if (lat, long) == (None, None):
#             return Response(content="Lat/Long not found for supplied address", status_code=500)
#         else:
#             location.point = Point(long, lat)

#     key = {'point': location.point}
#     action = "inserted"
#     # get the weeds already present at this location
#     old_loc = loc_db.find_one(key)
#     if old_loc is not None:
#         action = "updated"
#         old_loc = Location(**old_loc)
#         previous_weeds = old_loc.weeds_present
#         location.weeds_present.extend(previous_weeds)

#     # update the location if it is already present within the DB
#     id = loc_db.update(key, location.dict(), upsert=True)
#     print("+" * 10)
#     print(action)
#     # p.pprint(location.dict())
#     print("+" * 10)


# def delete(loc_db: Collection, location: Location):
#     if (location.lat, location.long) == (None, None):
#         lat, long = get_lat_long_from_address(location.name)
#         if (lat, long) == (None, None):
#             return Response(content="Lat/Long not found for supplied address", status_code=500)
#         else:
#             location.lat, location.long = lat, long
#     key = {'lat': location.lat, 'long': location.long}
#     deleted_count = loc_db.delete_one(key).deleted_count
#     if deleted_count == 0:
#         return Response(status_code=status.HTTP_204_NO_CONTENT)
#     else:
#         print("-" * 10)
#         print("deleted")
#         # p.pprint(location.dict())
#         print("-" * 10)
#         return Response(status_code=status.HTTP_200_OK)


# def add_weed(loc_db: Collection, lat: float, long: float, weed_instance: WeedInstance):
#     l = loc_db.find_one({"lat": lat, "long": long})
#     location = Location(**l)
#     location.add_weed(weed_instance)


def mark_weed_as_removed():
    pass


def mark_weed_as_replaced():
    pass
