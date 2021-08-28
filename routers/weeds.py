import logging
import uuid

from Models.WeedInstance import WeedInstance
from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from typing import List, Optional

from Models.Council import Council 
from Models.Location import Location
from Models.GeoJSONPoint import GeoJSONPoint

import routers.councils

from db.session import database_instance

router = APIRouter(
    prefix="/weeds",
    tags=["weeds"],
    responses={404: {"description": "Not found"}}
)

log = logging.getLogger("backend-logger")


# @router.get("/locations", response_model=List[Location])
@router.get("/", response_model=List[Location])
def get_all_locations(request: Request):
    """
    Return all locations that exist within the collection
    """
    weeds_collection = request.app.state.db.data.weeds
    res = weeds_collection.find()

    if res is None:
        raise HTTPException(status_code=404, detail="Could not find")

    return [WeedInstance(**i) for i in res] 

@router.post("/add", response_model=List[WeedInstance])
async def add_weed(request: Request, weed_id: int, discovery_date: str, removed: bool, 
                        removal_date: Optional[str], replaced: bool, replaced_species: Optional[str], 
                        image_filename: Optional[str], file: UploadFile = File(...)):
    """Adds a weed instance"""
    # -- async def upload(user: User = Depends(), file: UploadFile = File(...)):

    weeds_collection = request.app.state.db.data.weeds

    weed = WeedInstance({"weed_id": weed_id, "discovery_date": discovery_date, 
                "removed": removed, "removal_date": removal_date, "replaced": replaced, 
                "replaced_species": replaced_species, "image_filename": image_filename})

    new_filename = uuid.uuid4()

    try:
        with open(f"file/{new_filename}", "wb") as new_file: 
            new_file.write(file.file.read())

        weed.image_filename = new_filename
        weeds_collection.insert_one(weed.dict())

    except Exception as e:
        log.error(f"Failed to add weed - {e}")
        raise HTTPException(404)

    return True