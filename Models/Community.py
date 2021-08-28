from typing import List

from Models.Council import Council
from Models.Task import Task

class Community(Council):
    """
    Model to encapsulate communities which may / may not 
    have vague perimeters, or capture users which are not 
    within a specific area (online communities?)
    """

    #aditional to Council
    community_name: str
    community_tasks: List[Task]