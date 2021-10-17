from typing import List, Optional
from pydantic import Field, BaseModel

from Models.Council import Council
from Models.User import User


class Landcare(BaseModel):
    id: str = Field(..., alias='_id')
    _id: str
    boundary: Optional[dict]
    state: str 
    area_desc: str 
    nrm_id: int 
    nlp_mu: str 
    shape_area: float 
    shape_len: float
