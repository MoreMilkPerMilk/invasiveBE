from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon
from pydantic import BaseModel
from typing import List, Optional

from Models.Person import Person
from Models.Location import Location

class Task(BaseModel):
    """
    Encapsulates a task assigned to a user. 
    This task may be owned by a council / community.
    """
    id: int
    task_name: str 
    person: Person
    task_description: str 
    task_polygon: Optional[GeoJSONMultiPolygon]
    task_polygon_includes: Optional[List[GeoJSONMultiPolygon]]