from fastapi import APIRouter, Request, HTTPException
from typing import List

from ..Models.Council import Council 
from ..Models.Location import Location

import locations

from db.session import database_instance

router = APIRouter(
    prefix="/councils",
    tags=["councils"],
    responses={404: {"description": "Not found"}}
)


