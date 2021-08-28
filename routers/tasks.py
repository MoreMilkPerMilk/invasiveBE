from typing_extensions import ParamSpecKwargs
from fastapi import APIRouter, Request, HTTPException
from typing import List
from bson.objectid import ObjectId

from Models.Task import Task

import routers.locations as locations

from db.session import database_instance

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "bad input"}
    }
)

@router.get("/", response_model=List[Task])
def get_tasks(request: Request) -> List[Task]:
    """
        Returns all tasks in collection
    """
    tasks_collection = request.app.state.db.data.tasks 

    res = tasks_collection.find()

    if res is None:
        raise HTTPException(404)

    return [Task(**t) for t in res]

@router.get("/{_id}", response_model=Task)
def get_task_by_id(request: Request, _id: str = None):
    """
        Get task by id
    """
    tasks_collection = request.app.state.db.data.tasks 

    res = tasks_collection.find_one({"_id": ObjectId(_id)})
    # print(res)

    if res is None: 
        raise HTTPException(404)

    return Task(**res) #?

@router.post("/add")
def add_task(request: Request, task: Task = None):
    """
        Add task to collection    
    """
    tasks_collection = request.app.state.db.data.tasks 

    res = tasks_collection.insert_one(task.dict(by_alias=True))

    if res is None: 
        raise HTTPException(404)

    # return {"inserted_id": res.inserted_id}



@router.post("/delete")
def delete_task(request: Request, task_id: str = None):
    """
        Deletes a task in collection by it's ObjectId()
    """
    tasks_collection = request.app.state.db.data.tasks 
    res = tasks_collection.delete_many({"_id": ObjectId(task_id)})

    if res is None:
        raise HTTPException(400)

    if res.deleted_count == 0:
        raise HTTPException(404)