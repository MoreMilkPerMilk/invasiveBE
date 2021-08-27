from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon
from pydantic import BaseModel

from Models.Person import Person
from Models.Location import Location

class Task(BaseModel):
    """
    Encapsulates a task assigned to a user. 
    This task may be owned by a council / community.
    """

    task_name: str 
    person: Person
    task_description: str 
    task_polygon: GeoJSONMultiPolygon
