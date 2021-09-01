from pydantic import BaseModel, Field
from typing import List, Optional

# from Models.Person import Person
# from Models.Community import Community
# from Models.Council import Council
# from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon

# import Models
import Models.Council
import Models.Community
import Models.Person

class Task(BaseModel):
    """
    Encapsulates a task assigned to a user. 
    This task may be owned by a council / community.
    """
    id: str = Field(..., alias='_id')
    _id: str
    name: str 
    person: Models.Person.Person
    description: str 
    community: Optional[Models.Community.Community]
    council: Optional[Models.Council.Council]