import logging
import pprint
from typing import *

import uvicorn
from fastapi import FastAPI, Response, status

import LocationService
from DatabaseService import *
from Models.Location import Location

app = FastAPI()
client = connect_to_mongodb()
p = pprint.PrettyPrinter(sort_dicts=False)
log = logging.getLogger("location-logger")
loc_db = client['locations']
species_db = client['species']
weeds_db = client['weed_instances']


# @app.get("/locations", response_model=List[Location])
@app.get("/locations", response_model=List[Location])
def get_all_locations():
    """
    Return all locations that exist within the databases
    """
    result = list()
    for item in loc_db.find():
        try:
            result.append(Location(**item))
        except:
            result.append(item)
    return [x.dict() for x in result]


@app.post("/locations/add")
def add_location(location: Location):
    """
    Adds/Updates a location. Supply address name or lat/long.
    If lat/long already exist, merge the two lists of weeds.
    """
    if (location.lat, location.long) == (None, None):
        lat, long = LocationService.get_lat_long_from_address(location.name)
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


@app.post("/locations/delete")
def delete_location(location: Location):
    if (location.lat, location.long) == (None, None):
        lat, long = LocationService.get_lat_long_from_address(location.name)
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


# @app.get("/locations/{radius}")
# def get_nearby_locations(radius: float, response: Response, lat: Optional[float] = None, long: Optional[float] = None, addr: Optional[str] = None):
#     """
#     Return locations that are within a given radius (m). Supply either Lat/Long or Address. Lat/Long is prioritised.
#     """
#     if addr is not None:
#         lat, long = LocationService.get_lat_long_from_address(addr)
#         if (lat, long) == (None, None):
#             response.status_code = status.HTTP_400_BAD_REQUEST
#     else:


if __name__ == '__main__':
    uvicorn.run("BackendController:app", host='0.0.0.0', port=8000, reload=True)
