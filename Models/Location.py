from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional
from Models.WeedInstance import WeedInstance


class Location(BaseModel):
    _id: str
    name: str
    lat: Optional[float] = None
    long: Optional[float] = None
    weeds_present: Optional[List[WeedInstance]] = []




