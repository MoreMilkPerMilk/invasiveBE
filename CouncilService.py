import DatabaseService
import json
import pymongo
import logging

from geojson import MultiPolygon
from geojson import Point
from typing import List, Optional
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from Models.WeedInstance import WeedInstance
from Models.Council import Council
from Models.Species import Species
from Models.Location import Location

log = logging.getLogger("council-logger")


def get_by_abbreviated_name(council_collection: Collection, abb_name: str) -> Optional[Council]:
    """Gets council by abbreviated name"""
    q = council_collection.find_one({"abbreviated_name": abb_name})

    if not q.alive() or q is None:
        return None 

    return Council(**q)

def set_unique_keys(council_collection: Collection):
    """Sets council_collection to be uniquely identified by 'name' ASC"""
    council_collection.create_index(
        [("name", pymongo.ASCENDING)],
        unique=True
    )

def get_all_councils(council_collection: Collection) -> List[Council]:
    """Gets all the councils."""
    return [Council(**c) for c in council_collection.find()]

def get_council_from_location(council_collection: Collection, location: Location):
    """Get a council from a location."""
    councils = council_collection.find({"boundary":{"$geoIntersects":{"$geometry": location.point}}})

    if councils is None:
        log.error("get_council_from_location() - councils is None")

    res = [Council(**c) for c in councils]

    if len(res) > 1:
        log.error("get_council_from_location() - more than one council found?")
        log.error([Council(**c) for c in councils])
    
    return res[0]

def get_council_by_id(council_collection: Collection, id: int = None):
    """Get a Council by id"""
    res = council_collection.find_one({"_id": id})
    
    if res is None:
        return None
    
    return Council(**res)

# def find_council_for_location(council_collection: Collection, point: Point) -> Council:
#     council_collection.find

def create_council_collections_from_geojson(council_collection: Collection, geojson_filename: str):
    """Adds Councils from geojson file converted from data.gov"""
    with open(geojson_filename, "r") as geojson_f:
        geojson = json.load(geojson_f)

    if len(geojson) == 0:
        raise Exception(f"Could not open geojson file {geojson_filename}")

    for feature in geojson['features']:
        print(f"Adding {prop['LGA']} to Councils")
        prop = feature['properties']
        my_polygon = MultiPolygon(feature['geometry']['coordinates'])
        councilJson = {"name": prop['LGA'], 
                        "lga_code": int(prop['LGA_CODE']), 
                        "abbreviated_name": prop['ABBREV_NAME'],
                        "area_sqkm": float(prop['CA_AREA_SQKM']),
                        "boundary": MultiPolygon(feature['geometry']['coordinates']), #unnecessary
                        "species_occuring": [],
                        "locations": []}

        council = Council(**councilJson)

        try:
            council_collection.insert_one(council.dict()) 
        except Exception as e:
            print(f"Failed to add council {prop['LGA']}")
            print(e)


    # print("find")
    # print(get_all_councils(council_collection))


# def create_council_collection(client):
#     """
#         Creates a council collection
#     """
#     council_collection = client['councils']

#     base_council = Council(**{"_id": "1", "name": "test council", "locations": [], "species_occurring": [], "boundary": []})
#     print(base_council.dict())
#     council_collection.insert_one(base_council.dict())

#     for db_name in client.list_collection_names():
#         print(db_name)