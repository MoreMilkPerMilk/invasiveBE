from pydantic import BaseModel
from typing import List, Optional, Union

class Species(BaseModel):
    """
    A model representing a particular species of weed.
    Adapted from the api format of https://weeds.brisbane.qld.gov.au
    """
    species_id: int
    name: str
    species: str
    growth_form: str
    info: Optional[str]  # paragraph of extra info about the plant
    family: str
    native: bool
    flower_colour: List[str]
    flowering_time: Union[List[str], str]
    leaf_arrangement: Union[List[str], str]
    common_names: List[str]
    notifiable: bool  # whether or not the gov needs to know!
    control_methods: Union[List[str], str]
    replacement_species: Union[List[str], str]
    state_declaration: Union[List[str], str]
    council_declaration: str