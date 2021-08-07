from uuid import UUID
from pydantic import BaseModel
from typing import List
from Models.WeedInstance import WeedInstance


class Location(BaseModel):
    location_id: UUID
    name: str
    lat: float
    long: float
    weeds_present: List[WeedInstance]




