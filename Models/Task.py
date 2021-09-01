from pydantic import BaseModel, Field
from typing import List, Optional

from Models.Person import Person
from Models.Community import Community
from Models.Council import Council
from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon


class Task(BaseModel):
    """
    Encapsulates a task assigned to a user. 
    This task may be owned by a council / community.
    """
    id: str = Field(..., alias='_id')
    _id: str
    name: str 
    person: Person
    description: str 
    community: Optional[Community]
    council: Optional[Council]