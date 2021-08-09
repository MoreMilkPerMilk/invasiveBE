from pydantic import BaseModel
from typing import List

class Species(BaseModel):
    """
    A model representing a particular species of weed.
    Adapted from the api format of https://weeds.brisbane.qld.gov.au
    """
    _id: int
    name: str
    info: str  # paragraph of extra info about the plant
    family: str
    native: bool
    common_names: List[str]
    notifiable: bool  # whether or not the gov needs to know!
    species_name: str
    control_methods: List[str]
    replacement_species: List[str]
