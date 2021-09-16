from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum, IntEnum

from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon
from Models.WeedInstance import WeedInstance
from Models.Location import Location



class Status(str, Enum):
    closed = 'closed'
    open = 'open'


class Report(BaseModel):
    """
    Encapsulates a report associated with a number of WeedInstances. 
    This will be used for Councils to collaborate with users and their 
    weed captures.
    """
    id: str = Field(..., alias='_id')
    _id: str
    name: str #unsure 
    status: Status 
    locations: List[Location]
    notes: str 
    polygon: Optional[GeoJSONMultiPolygon] = None
    images: Optional[List[str]] = None
    

    #idk images back from WeedInstances?
