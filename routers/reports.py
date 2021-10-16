from Models.GeoJSONMultiPolygon import GeoJSONMultiPolygon
import logging
import uuid
import pymongo
import geojson
import shapely
from shapely.geometry import shape
# import shapely.geometry.Point as ShapelyPoint
import shapely.geometry as shapegeo

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

def process_polygon(report: Report):
    if len(report.locations) >= 3:
        polygon = geojson.Polygon([(loc.point.coordinates[0], loc.point.coordinates[1]) for loc in report.locations])
        print(f"polygon = {polygon}")
        # print(polygon.)

        polygon = shapely.geometry.Polygon([(loc.point.coordinates[0], loc.point.coordinates[1]) for loc in report.locations])
        polygon = to_square(polygon)
        # polygon = polygon.map(to_square)

        # print(polygon['geometry'])
        print(polygon)

        # report.polygon = GeoJSONMultiPolygon(**{'coordinates': polygon.coords[:]})
        coords = [[[float(i[0]), float(i[1])] for i in shapely.geometry.Polygon(polygon.boundary).exterior.coords[:-1]]]
        print(coords)
        report.polygon = GeoJSONMultiPolygon(**{'coordinates': coords})
    
    return report

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

    # reports_collection 

@router.post("/add", response_model=Report)
def add_a_report(request: Request, report: Report):
    """
        Add a report, backend will calculate bounding polygon.
    """
    reports_collection = request.app.state.db.data.reports

    # reports = get_all_reports(request)

# doesn't actually merge, just outputs if merge possible to console.
    # if len(reports) == 0:
    #     print("no reports to merge")
    # else:
    #     for report_ in reports:
    #         for loc in report.locations:
    #             point = shapegeo.Point(loc.point.coordinates[0], loc.point.coordinates[1])
    #             polygon = shape(report.polygon.to_geojson())
    #             if polygon.contains(point):
    #                 print("POSSIBLE MERGE")
    #                 print(report_)

    if report.polygon is not None and False:
        print("hmm chosen to supply polygon") #ignored
    elif len(report.locations) >= 3:
        polygon = geojson.Polygon([(loc.point.coordinates[0], loc.point.coordinates[1]) for loc in report.locations])
        print(f"polygon = {polygon}")
        # print(polygon.)

        polygon = shapely.geometry.Polygon([(loc.point.coordinates[0], loc.point.coordinates[1]) for loc in report.locations])
        polygon = to_square(polygon)
        # polygon = polygon.map(to_square)

        # print(polygon['geometry'])
        print(polygon)

        # report.polygon = GeoJSONMultiPolygon(**{'coordinates': polygon.coords[:]})
        coords = [[float(i[0]), float(i[1])] for i in shapely.geometry.Polygon(polygon.boundary).exterior.coords[:-1]]
        print(coords)
        report.polygon = GeoJSONMultiPolygon(**{'coordinates': coords}) #negative one without repeat
    
    try:    
        res = reports_collection.insert_one(report.dict(by_alias=True))
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(404, "Tried to insert a duplicate.")

    if res is None:
        raise HTTPException(404)

    d = report.dict(by_alias=True)
    d['_id'] = res.inserted_id

    return d
        
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
    
    report = process_polygon(report)

    reports_collection.replace_one(key, report.dict(by_alias=True), upsert=True)

@router.put("/addphotolocationbyid", response_model=Report)
def add_photolocation_to_report(request: Request, report_id: str, location_id: str):
    """
        Adds a Photo-Location pair to a Report
    """
    reports_collection = request.app.state.db.data.reports
    photolocations_collection = request.app.state.db.data.photolocations
    
    key = {"_id": report_id}
    res = reports_collection.find_one(key)

    if res is None:
        raise HTTPException(404, detail="report not found")

    report = Report(**res)

    location_res = photolocations_collection.find_one({"_id": location_id})

    if location_res is None: 
        raise HTTPException(404, detail="location not found")

    location = PhotoLocation(**location_res)

    report.add_location(location)

    report = process_polygon(report)
    reports_collection.replace_one(key, report.dict(by_alias=True), upsert=True)

    return report

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
    pusher_client.trigger(report.name, "update", {'message': message})