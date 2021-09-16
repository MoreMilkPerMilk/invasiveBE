from pydantic import BaseModel, Field
from typing import List, Optional

from Models.Person import Person
from Models.Community import Community
from Models.Council import Council
from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon


class Event(BaseModel):
    """
    Encapsulates a event assigned to a user. 
    This event may be owned by a council / community.
    """
    id: str = Field(..., alias='_id')
    _id: str
    name: str 
    person: Person
    description: str 
    community: Optional[Community]
    council: Optional[Council]