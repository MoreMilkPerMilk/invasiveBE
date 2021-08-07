from pydantic import BaseModel
from uuid import UUID
from datetime import date


class WeedInstance(BaseModel):
    instance_id: UUID  # id for this specific instance
    species_id: int  # lookup via Species model
    discovery_date: date

    removed: bool
    removal_date: date

    replaced: bool
    replaced_species_id: int  # lookup via Species model
