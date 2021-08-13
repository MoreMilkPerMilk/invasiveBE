from geopy.geocoders import Nominatim

import logging
from pymongo.collection import Collection
from Models.WeedInstance import WeedInstance
from Models.Location import Location

log = logging.getLogger("location-logger")


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