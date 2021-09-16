# staff, person,
# first last, day joined, number of species identified, species tagged,
from pydantic import BaseModel, Field
from typing import Optional, List
from Models.WeedInstance import WeedInstance
from Models.Location import Location

class Person(BaseModel):
    person_id: int #TODO: change to field alias
    # id: str = Field(..., alias='_id')
    # _id: str

    first_name: str
    last_name: str
    date_joined: str
    count_identified: int
    previous_tags: List[WeedInstance]
    location: Optional[Location] = None

    def add_identification(self, instance: WeedInstance):
        self.previous_tags.append(instance)
        self.count_identified = len(self.previous_tags)

