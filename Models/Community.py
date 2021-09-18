from typing import List, Optional
from pydantic import Field, BaseModel

from Models.Council import Council
from Models.User import User


class Community(BaseModel):
    """
    Model to encapsulate communities which may / may not 
    have vague perimeters, or capture users which are not 
    within a specific area (online communities?)
    """
    id: str = Field(..., alias='_id')
    _id: str
    name: str
    events: Optional['List[Event]']= [] # needs '' for update_forward_refs() to fix circular dependency
    members: Optional[List[User]] = []
    boundary: Optional[dict]
    suburbs: Optional[List[str]] = []
    councils: Optional[List[str]] = []


    def add_user(self, user: User):
        """Add a user to the community"""
        if len(self.members) == 0:
            self.members = []

        self.members.append(user)

    
    def add_event(self, event: 'Event'): # LEAVE 'Event' as update_forward_refs()
        """Adds a event to this Community"""
        if len(self.events) == 0:
            self.events = []

        self.events.append(event)

from Models.Event import Event
Community.update_forward_refs()
