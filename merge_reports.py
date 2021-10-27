import requests
import os
import json
import time
from Models.Report import Report
from routers.reports import process_polygon
from Models.Species import Species 
import numpy as np

from bson.objectid import ObjectId

from Models.GeoJSONPoint import GeoJSONPoint
from Models.PhotoLocation import PhotoLocation
from routers.photolocations import location_near

from shapely.geometry import LineString
from shapely.ops import transform
from functools import partial
import pyproj

# import bson

# BASE_URL = "http://invasivesys.uqcloud.net"
BASE_URL = 'http://35.244.125.224'


START_DIR = "/home/djamahl/Documents/Code/resnet_weeds/ImageNet_ResNet_Tensorflow2.0/images_test/"

def add_photolocation(location: PhotoLocation):
    print("add", location)
    # location.image_filename
    # values = {'DB': 'photcat', 'OUT': 'csv', 'SHORT': 'short'}

    #create
    # print(BASE_URL + "/photolocations/create")
    print(location.dict(by_alias=True))
    r = requests.post(BASE_URL + "/photolocations/create", headers={'Content-Type': "application/json; charset=UTF-8"}, data=json.dumps(location.dict(by_alias=True), indent=4))
    # print(r.body)
    print(r.text)

    # print("\nUPLOAD\n")
    # print("file path", START_DIR + location.image_filename)

    parameters = {}
    files = {'file': open(START_DIR + location.image_filename,'rb')}
    url = BASE_URL + f"/photolocations/uploadphoto/{location.id}"
    # print(url)
    r = requests.post(url, files=files)
    # print(r.text)
    j = json.loads(r.text)
    j['_id'] = j['id']
    time.sleep(1)
    return PhotoLocation(**j)

# def create_report()
def find_species(search_term):
    url = BASE_URL + f"/species/search/{search_term}"
    # print("url", url)

    r = requests.get(url)
    # print(r.text)

    j = json.loads(r.text)

    print(f"found {len(j)} species")
    
    if len(j) != 1:
        print("error")
        print(j)
        exit()

    # print("json decoded", j[0])
    species = Species(**j[0])

    time.sleep(1)

    return species

def add_report(report: Report):
    print("create report", report)
    #create
    print(BASE_URL + "/reports/add")
    # print("dict", report.dict(by_alias=True))
    print("json", json.dumps(report.dict(by_alias=True), indent=4))
    # print(r.body))
    r = requests.post(BASE_URL + "/reports/add", headers={'Content-Type': "application/json; charset=UTF-8"}, data=json.dumps(report.dict(by_alias=True), indent=4))
    # print(r.body)
    print("RETURNED", r.text)
    return Report(**json.loads(r.text))

def add_location_to_report(report: Report, location: PhotoLocation):
    print("add location to report", report, location)

    update_report(reports[j])
    params = {'report_id': report.id, 'location_id': location.id}
    url = BASE_URL + f"/reports/addphotolocationbyid?report_id={report.id}&location_id={location.id}"
    print(url)
    r = requests.put(url, params=params)

    print(r.text)
    time.sleep(1)

    return Report(**json.loads(r.text))

def update_report(report: Report):
    print("update report", report, location)

    params = {'report_id': report.id}
    url = BASE_URL + f"/reports/update"
    print(url)
    # r = requests.put(url, params=params)
    print(report.dict(by_alias=True))
    r = requests.put(url, params=params, headers={'Content-Type': "application/json; charset=UTF-8"}, data=json.dumps(report.dict(by_alias=True), indent=4))


    print("returns", r.text)
    time.sleep(1)

    return Report(**json.loads(r.text))

def get_reports():
    print("get reports")
    url = BASE_URL + f"/reports/"
    r = requests.get(url)

    with open("backup.json", "w") as f:
        f.write(r.text)
        f.close()

    # list = json.loads(r.text)
    return [Report(**s) for s in json.loads(r.text)]




# print(get_reports())

reports = get_reports()

reports_done = [False for i in range(len(reports))]

project = partial(
    pyproj.transform,
    pyproj.Proj('EPSG:4326'),
    pyproj.Proj('EPSG:32633'))

for i in range(len(reports)):
    report = reports[i]

    # print(f"{report.name} has {len(report.locations)} locations")


    if len(report.locations) == 0:
        # print("report has no locations", report.name)
        pass

    elif len(report.locations) == 1:
        # print("report has one location", report.name)

        loc = report.locations[0]
        # furthest = 15
        
        for j in range(i + 1, len(reports)):
            report2 = reports[j]

            if len(report2.locations) == 1:
                location = report2.locations[0]
                line1 = LineString([(loc.point.coordinates[1], loc.point.coordinates[0]), 
                                (location.point.coordinates[1],location.point.coordinates[0])])
                line2 = transform(project, line1)

                if line2.length <= 15 and report.species_id == report2.species_id:
                    print("close!")
                    report.add_location(report2.locations[0])
                    report = process_polygon(report)
                    reports[i] = report
                    reports[j].locations = []
                    report2 = reports[j]
                    print("added")
                    # print(report)
                    # print(f"{report.name} has {len(report.locations)}" locations})
                    print(f"{report.name} has {len(report.locations)} locations")
                    update_report(reports[j])

    update_report(report)


    
    # else:
    #     print("report has many locations", report.name)


    # reports_done[i] = True
    # print(repo)
# 