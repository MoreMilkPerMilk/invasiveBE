import uuid

from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional


class WeedInstance(BaseModel):
    _id: str  # id for this specific instance
    uuid: uuid.UUID
    species_id: int  # lookup via Species model
    discovery_date: str

    removed: bool
    removal_date: Optional[str]

    replaced: bool
    replaced_species: Optional[str]  # lookup via Species model

    image_filename: Optional[str]
