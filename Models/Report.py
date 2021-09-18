from Models.Species import Species
from Models.PhotoLocation import PhotoLocation
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum, IntEnum

from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon
from Models.PhotoLocation import PhotoLocation

class Status(str, Enum):
    """
        Status of the Report (open / closed)
    """
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
    species_id: str
    status: Status 
    locations: List[PhotoLocation]
    notes: str 
    polygon: Optional[GeoJSONMultiPolygon] = None
    pusher_channel: Optional[str]

    #idk images back from WeedInstances?

    def add_location(self, location: PhotoLocation):
        """
            Adds location to this Report's locations
        """
        if self.locations is None:
            self.locations = []

        self.locations.append(location)