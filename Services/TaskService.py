import pymongo 

from pymongo.collection import Collection

from Models.Task import Task

def set_unique_keys(task_collection: Collection):
    """Sets task_collection to be uniquely identified by 'task_id' ASC"""
    task_collection.create_index(
        [("task_id", pymongo.ASCENDING)],
        unique=True
    )

def add_task(task_collection: Collection, task: Task):
    """Add task to task_collection"""
    