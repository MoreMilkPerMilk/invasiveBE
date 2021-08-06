from pydantic import BaseModel


class Species(BaseModel):
    """
    A model representing a particular species of weed.
    Adapted from the api format of https://weeds.brisbane.qld.gov.au
    """
    id: int
    name: str
    family: str
    native: bool
    common_names: [str]
    notifiable: bool  # whether or not the gov needs to know!
    species_name: str
    control_methods: [str]
    replacement_species: [str]
