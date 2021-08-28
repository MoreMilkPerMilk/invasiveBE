from pydantic import BaseModel, Field
from typing import List, Optional

from Models.Person import Person
from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon


class Task(BaseModel):
    """
    Encapsulates a task assigned to a user. 
    This task may be owned by a council / community.
    """
    id: str = Field(..., alias='_id')
    _id: str
    task_name: str 
    person: Person
    task_description: str 
    task_polygon: Optional[GeoJSONMultiPolygon]
    task_polygon_includes: Optional[List[str]]