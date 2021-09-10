# staff, person,
# first last, day joined, number of species identified, species tagged,
from pydantic import BaseModel, Field
from typing import Optional, List
from Models.WeedInstance import WeedInstance
from Models.Location import Location

from enum import Enum, IntEnum


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
    weeds: List[WeedInstance] 
    notes: str 
    

    #idk images back from WeedInstances?
