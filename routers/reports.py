import logging
import uuid

from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from typing import List, Optional

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