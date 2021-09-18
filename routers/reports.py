from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon
import logging
import uuid
import pymongo
import geojson
import shapely

from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from typing import List, Optional
from pymongo.collection import Collection
from shapely.geometry import Point
from math import sqrt

from Models.Council import Council 
from Models.PhotoLocation import PhotoLocation
from Models.GeoJSONPoint import GeoJSONPoint
from Models.Report import Report

from db.session import database_instance

PADDING = 0.1 # 10% padding on report boundary

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}}
)

log = logging.getLogger("backend-logger")

def set_unique_keys(reports_collection: Collection):
    """
        Sets reports_collection to be uniquely identified by 'name' ASC
    """
    reports_collection.create_index(
        [("name", pymongo.ASCENDING)],
        unique=True
    )

def to_square(polygon):
    """
        For shapely boundaries
        https://gis.stackexchange.com/questions/374864/creating-a-square-buffer-around-a-shapely-polygon
    """
    minx, miny, maxx, maxy = polygon.bounds
    
    # get the centroid
    centroid = [(maxx+minx)/2, (maxy+miny)/2]
    # get the diagonal
    diagonal = sqrt((maxx-minx)**2+(maxy-miny)**2)
    
    return Point(centroid).buffer(diagonal/2, cap_style=3)

@router.get("/", response_model=List[Report])
def get_all_reports(request: Request):
    """
    GET all the reports in the collection
    """
    reports_collection = request.app.state.db.data.reports 
    res = reports_collection.find()

    if res is None:
        raise HTTPException(404)

    return [Report(**i) for i in res]

@router.put("/update", response_model=Report)
def update_a_report(request: Request, report_id: str, report: Report):
    """
    Update a given report
    """
    reports_collection = request.app.state.db.data.reports

    reports_collection 

@router.post("/add", response_model=Report)
def add_a_report(request: Request, report: Report):
    """
        Add a report, backend will calculate bounding polygon.
    """

    if report.polygon is not None:
        log.print("hmm chosen to supply polygon")
    else:
        polygon = geojson.Polygon([(loc.point.coordinates[0], loc.point.coordinates[1]) for loc in report.locations])
        print(f"polygon = {polygon}")

        polygon = shapely.geometry.Polygon([(loc.point.coordinates[0], loc.point.coordinates[1]) for loc in report.locations])
        # polygon['geometry'] = polygon['geometry'].map(to_square)
        polygon = polygon.map(to_square)

        print(polygon['geometry'])
        
@router.put("/addphotolocation", response_model=Report)
def add_location_to_report(request: Request, report_id: str, location: PhotoLocation):
    """
        Adds a Photo-Location pair to a Report
    """
    reports_collection = request.app.state.db.data.reports
    
    key = {"_id": report_id}
    res = reports_collection.find_one(key)

    if res is None:
        raise HTTPException(404)

    report = Report(**res)
    report.add_location(location)

    reports_collection.replace_one(key, report.dict(), upsert=True)

@router.put("/sendpushnotification")
def send_push_notification(request: Request, report_id: str, message: str):
    """
        Sends a push notification to all users related to a report
    """
    reports_collection = request.app.state.db.data.reports

    res = reports_collection.find_one({"_id": report_id})

    if res is None:
        raise HTTPException(404)

    report = Report(**res)

    pusher_client = request.app.state.pusher_client
    pusher_client.trigger("council-report-updates", report.name, {'message': message})