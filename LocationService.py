from geopy.geocoders import Nominatim

import logging
from pymongo.collection import Collection

log = logging.getLogger("location-logger")


def get_lat_long_from_address(address: str) -> (float, float):
    geolocator = Nominatim(user_agent="invasiveML")
    loc = geolocator.geocode(address)
    lat, long = None, None
    try:
        lat, long = loc.latitude, loc.longitude
    except:
        log.error(f"Latitude and Longitude couldn't be found for addr:{address}")
    return lat, long

# def get_address_within_radius(locations_db: Collection, radius: float):
#     locations_db.find().wh