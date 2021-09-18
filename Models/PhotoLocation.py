from Models.GeoJSONPoint import GeoJSONPoint
import uuid
from uuid import UUID
from pydantic import BaseModel, Field
from geojson import Point
from typing import List, Optional

class PhotoLocation(BaseModel):
    id: str = Field(..., alias='_id')
    _id: str
    image_filename: str
    point: GeoJSONPoint