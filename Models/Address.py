from pydantic import BaseModel, Field
from typing import List, Optional


class Address(BaseModel):
    address: str