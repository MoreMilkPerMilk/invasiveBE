from pydantic import BaseModel
from typing import List
from geojson import MultiPolygon

class GeoJSONMultiPolygon(BaseModel):
    """
        pydantic version of geojson MultiPolygon for FastAPI
    """
    coordinates: List[List[float]]
    type = 'MultiPolygon'

    def to_geojson(self):
        return MultiPolygon(self.coordinates)