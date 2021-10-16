# staff, person,
# first last, day joined, number of species identified, species tagged,
from Models.Report import Report
from pydantic import BaseModel, Field
from typing import Optional, List
from Models.Report import Report
from Models.PhotoLocation import PhotoLocation

class User(BaseModel):
    # person_id: int #TODO: change to field alias
    id: str = Field(..., alias='_id')
    _id: str

    first_name: str
    last_name: str
    date_joined: Optional[int]
    reports: Optional[List[Report]]
    mac_address: Optional[str]
    added_details: bool

    def add_report(self, report: Report):
        """
            Add a report to this user
        """
        # self.reports.add(report)
        self.reports.append(report)