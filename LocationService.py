import pprint

from geopy.geocoders import Nominatim

import logging
from fastapi import Response, status
from pymongo.collection import Collection
from Models.WeedInstance import WeedInstance
from Models.Location import Location

log = logging.getLogger("location-logger")
p = pprint.PrettyPrinter(sort_dicts=False)


def get_all(loc_db: Collection):
    result = list()
    for item in loc_db.find():
        try:
            result.append(Location(**item))
        except:
            result.append(item)
    return [x.dict() for x in result]


def add(loc_db: Collection, location: Location):
    if (location.lat, location.long) == (None, None):
        lat, long = get_lat_long_from_address(location.name)
        if (lat, long) == (None, None):
            return Response(content="Lat/Long not found for supplied address", status_code=500)
        else:
            location.lat, location.long = lat, long

    key = {'lat': location.lat, 'long': location.long}
    action = "inserted"
    # get the weeds already present at this location
    old_loc = loc_db.find_one(key)
    if old_loc is not None:
        action = "updated"
        old_loc = Location(**old_loc)
        previous_weeds = old_loc.weeds_present
        location.weeds_present.extend(previous_weeds)

    # update the location if it is already present within the DB
    id = loc_db.update(key, location.dict(), upsert=True)
    print("+" * 10)
    print(action)
    p.pprint(location.dict())
    print("+" * 10)


def delete(loc_db: Collection, location: Location):
    if (location.lat, location.long) == (None, None):
        lat, long = get_lat_long_from_address(location.name)
        if (lat, long) == (None, None):
            return Response(content="Lat/Long not found for supplied address", status_code=500)
        else:
            location.lat, location.long = lat, long
    key = {'lat': location.lat, 'long': location.long}
    deleted_count = loc_db.delete_one(key).deleted_count
    if deleted_count == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        print("-" * 10)
        print("deleted")
        p.pprint(location.dict())
        print("-" * 10)
        return Response(status_code=status.HTTP_200_OK)


def get_lat_long_from_address(address: str) -> (float, float):
    geolocator = Nominatim(user_agent="invasiveML")
    loc = geolocator.geocode(address)
    lat, long = None, None
    try:
        lat, long = loc.latitude, loc.longitude
    except AttributeError:
        log.error(f"Latitude and Longitude couldn't be found for addr:{address}")
    return lat, long


def add_weed(loc_db: Collection, lat: float, long: float, weed_instance: WeedInstance):
    l = loc_db.find_one({"lat": lat, "long": long})
    location = Location(**l)
    location.add_weed(weed_instance)


def mark_weed_as_removed():
    pass


def mark_weed_as_replaced():
    pass
