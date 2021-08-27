from pydantic import BaseModel
from typing import List

class GeoJSONMultiPolygon(BaseModel):
    """
        pydantic version of geojson MultiPolygon for FastAPI
    """
    coordinates: List[float]
    type = 'MutiPolygon'