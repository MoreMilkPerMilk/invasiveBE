from typing import List, Optional
from pydantic import Field, BaseModel

from Models.Council import Council
from Models.Person import Person


class Community(BaseModel):
    """
    Model to encapsulate communities which may / may not 
    have vague perimeters, or capture users which are not 
    within a specific area (online communities?)
    """

    #aditional to Council
    id: str = Field(..., alias='_id')
    _id: str
    name: str
    tasks: Optional['List[Task]']= [] # needs '' for update_forward_refs() to fix circular dependency
    members: Optional[List[Person]] = []
    boundary: Optional[dict]
    suburbs: Optional[List[str]] = []
    councils: Optional[List[str]] = []


    def add_user(self, user: Person):
        """Add a user to the community"""
        if len(self.members) == 0:
            self.members = []

        self.members.append(user)

    
    def add_task(self, task: 'Task'): # LEAVE 'Task' as update_forward_refs()
        """Adds a task to this Community"""
        if len(self.tasks) == 0:
            self.tasks = []

        self.tasks.append(task)

from Models.Task import Task
Community.update_forward_refs()
