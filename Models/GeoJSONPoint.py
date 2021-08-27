from pydantic import BaseModel
from typing import List

class GeoJSONPoint(BaseModel):
    """
        pydantic version of geojson POINT for FastAPI
    """
    # {"coordinates": [-115.8..., 37.2...], "type": "Point"}
    coordinates: List[float]
    type = 'Point'