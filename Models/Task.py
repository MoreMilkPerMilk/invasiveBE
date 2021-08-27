from pydantic import BaseModel

from Models.Person import Person

class Task(BaseModel):
    """
    Encapsulates a task assigned to a user. 
    This task may be owned by a council / community.
    """

    task_name: str 
    person: Person
    