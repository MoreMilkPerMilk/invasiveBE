import uuid
from uuid import UUID
from pydantic import BaseModel, Field
from geojson import Point
from typing import List, Optional
from Models.WeedInstance import WeedInstance

class Location(BaseModel):
    id: str = Field(..., alias='_id')
    _id: str
    name: str
    # lat: Optional[float] = None
    # long: Optional[float] = None
    point: Optional[dict] = None
    weeds_present: Optional[List[WeedInstance]] = []

    def add_weed(self, weed_instance: WeedInstance):
        present = False
        for weed in self.weeds_present:
            if weed.uuid == weed_instance.uuid:
                present = True
                break

        if not present:
            self.weeds_present.append(weed_instance)



