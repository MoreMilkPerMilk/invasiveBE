import logging
import uuid
import pymongo

from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from typing import List, Optional
from pymongo import Collection

from Models.WeedInstance import WeedInstance
from Models.Council import Council 
from Models.Location import Location
from Models.GeoJSONPoint import GeoJSONPoint
from Models.Report import Report

from db.session import database_instance

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}}
)

log = logging.getLogger("backend-logger")

def set_unique_keys(reports_collection: Collection):
    """
        Sets reports_collection to be uniquely identified by 'point' ASC
    """
    reports_collection.create_index(
        [("name", pymongo.ASCENDING)],
        unique=True
    )

@router.get("/", response_mode=List[Report])
def get_all_reports(request: Request):
    """
    GET all the reports in the collection
    """
    reports_collection = request.app.state.db.data.reports 
    res = reports_collection.find()

    if res is None:
        raise HTTPException(404)

    return [Report(**i) for i in res]

@router.put("/{report_id}", response_model=Report)
def update_a_report(request: Request, report_id: str, report: Report):
    """
    Update a given report
    """
    reports_collection = request.app.state.db.data.reports 

@router.post("/add", response_model=Report)
def add_a_report(request: Request, report: Report):
    """
        Add a report, backend will calculate bounding polygon.
    """

    if report.polygon is not None:
        log.print("hmm chosen to supply polygon")
    else:
        # minimum bounding
        min = (float('inf'), float('inf'))
        max = (float('-inf'), float('-inf'))

        for location in report.locations:
            if point.