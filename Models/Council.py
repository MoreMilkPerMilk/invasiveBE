from geojson import MultiPolygon
from uuid import UUID
from pydantic import BaseModel, Field
from typing import List, Optional
from Models.Location import Location
from Models.WeedInstance import WeedInstance
from Models.Species import Species

class Council(BaseModel):
    """
    Model for decribing a council including geo boundary, 
    weed instance locations within the council boundary
    """
    id: str = Field(..., alias='_id')
    _id: str
    name: str
    # locations: List[Location] = [] #no longer
    species_occuring: Optional[List[Species]] = []
    boundary: Optional[dict]
    lga_code: int 
    abbreviated_name: str
    area_sqkm: float

    def add_occuring_species(self, species: Species):
        """Adds a species that occurs in this Council."""
        if species.species_id not in \
                [s.species_id for s in self.species_occuring]:
            self.weeds_occurring(species)

    def set_locations(self, locations: List[Location]):
        """Sets weed instance locations to this Council."""
        self.locations = locations
    
    def add_location(self, location: Location):
        """Add locations"""

    def set_boundary(self, boundary: MultiPolygon):
        """Sets the geo boundary for the council LGA."""
        self.boundary = boundary

    # def export(self):
    #     """Exports dictionary where locations and species_occuring export 
    #         as only a list of keys for the db."""
        
