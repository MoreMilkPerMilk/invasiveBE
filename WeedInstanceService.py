import pprint
import logging
import pymongo
import uuid

from fastapi import Response, status, UploadFile
from geopy.geocoders import Nominatim
from geojson import Point
from pymongo.collection import Collection
from typing import List, Optional, Tuple

from Models.WeedInstance import WeedInstance
from Models.Location import Location
from Models.Council import Council
from Models.GeoJSONPoint import GeoJSONPoint

log = logging.getLogger("location-logger")
# p = pprint.PrettyPrinter(sort_dicts=False)

def set_unique_keys(weed_collection: Collection):
    """Sets weed_collection to be uniquely identified by 'species_id' ASC"""
    weed_collection.create_index(
        [("name", pymongo.ASCENDING)],
        unique=True
    )

def add_weed(weed_collection: Collection, weed: WeedInstance, file: UploadFile) -> bool:
    """Add weed to weed_collection"""
    log.print("add weed")
    log.print(weed)
    log.print(weed.dict())
    
    new_filename = uuid.uuid4()

    try:
        with open(f"file/{new_filename}", "wb") as new_file: 
            new_file.write(file.file.read())

        weed.image_filename = new_filename
        weed_collection.insert_one(weed.dict())

    except Exception as e:
        log.error(f"Failed to add weed - {e}")
        return False

    return True

def get_weed_by_species_id(weed_collection: Collection, species_id: int) -> WeedInstance:
    """Gets a WeedInstance by a species_id"""
    