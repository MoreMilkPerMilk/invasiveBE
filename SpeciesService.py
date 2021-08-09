import json, requests
from typing import List

from fuzzywuzzy import fuzz
from pymongo.collection import Collection

import DatabaseService
from Models.Species import Species

WEED_URL = "https://weeds.brisbane.qld.gov.au/api/weeds"
client = DatabaseService.connect_to_mongodb()
species_db = client['species']

def get_govt_data_and_populate():
    client = DatabaseService.connect_to_mongodb()
    species_db = client['species']
    r = requests.get(WEED_URL)
    print(r.json())
    entries = []
    for s in r.json():
        entry = {
            "species_id": s["Nid"],
            "name": s["Name"],
            "species": s['Species name'],
            # "info":
            "family": s["Family"],
            "native": True if s["Native/Exotic"] == "Native" else False,  # thx aussie gov't
            "common_names": s["Common names"],
            "notifiable": True if s["Notifiable"] == "Yes" else False,
            "growth_form": s["Growth form"],
            "flower_colour": s["Flower colour"],
            "leaf_arrangement": s["Leaf arrangement"],
            "flowering_time": s["Flowering time"],
            "state_declaration": s["State declaration"],
            "council_declaration": s["Council declaration"],
            "control_methods": s["Control methods"],
            "replacement_species": s["Replacement species"],
        }
        species_db.insert_one(Species(**entry).dict())


def get_all_species_data() -> List[Species]:
    client = DatabaseService.connect_to_mongodb()
    species_db = client['species']
    result = []
    for species in species_db.find():
        result.append(Species(**species))
    return result


def get_species_by_id(species_db: Collection, id: int) -> Species:
    """
    Find plant based on specific id (brisbane weed database)
    """
    species_dict = species_db.find_one({"species_id": id})
    return Species(**species_dict)


def get_species_by_name(species_db: Collection, name: str) -> [Species]:
    """
    Fuzzy search finding of species entries by name
    """
    results = []
    for species in species_db.find():
        if fuzz.ratio(name, species['name']) > 75:  # fuzzy search threshold
            results.append(species)

    return results


# get_govt_data_and_populate() ## DO NOT RUN THIS UNLESS REPOPULATING THE WHOLE DB
# print(get_all_species_data())
# print(get_species_by_id(species_db, 73))
print(get_species_by_name(species_db, "chinee apple"))
