import requests
import os
import json
import time
from Models.Report import Report
from Models.Species import Species 
import numpy as np

from bson.objectid import ObjectId

from Models.GeoJSONPoint import GeoJSONPoint
from Models.PhotoLocation import PhotoLocation
from routers.photolocations import location_near

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

    params = {'report_id': report.id, 'location_id': location.id}
    url = BASE_URL + f"/reports/addphotolocationbyid?report_id={report.id},location_id={location.id}"
    print(url)
    r = requests.put(url, params=params)

    print(r.text)
    time.sleep(1)

    return Report(**json.loads(r.text))

# def (location: PhotoLocation):

# -27.083328, 151.992788
# -28.210155, 153.068367 
lat_bnds = (-27.083328, -28.210155)
long_bnds = (151.992788, 153.068367)

added = 0

for dir in os.listdir(START_DIR):
    print("dir = ", dir)
    species = find_species(dir)
    report_len = 0
    report_num = 0
    report_num_samples = np.random.randint(1, 10)
    report = Report(**{'_id': str(ObjectId()),'name': f"{dir} example report no. {report_num}", 'species_id': species.species_id, 'status': "open" if np.random.randint(0, 1) == 0 else "closed", "notes": f"an example generated report with {report_num_samples} PhotoLocations", 'locations': []})
    report = add_report(report)

    # exit()

    for file in os.listdir(START_DIR + "/" + dir):
        filename = f"{dir}/{file}"

        if report_len > report_num_samples: #new report
            report_num += 1
            report_len = 0
            print("new report")
            report_num_samples = np.random.randint(1, 10)
            report = Report(**{'_id': str(ObjectId()),'name': f"{dir} example report no. {report_num}", 'species_id': species.species_id, 'status': "open" if np.random.randint(0, 1) == 0 else "closed", "notes": f"an example generated report with {report_num_samples} PhotoLocations", 'locations': []})
            report = add_report(report)
            # exit()
        elif report_num > 4:
            break

        if np.random.rand() > 0.1:
            added += 1
            print("file", filename)
            if report_len == 0:
                lat = np.random.uniform(lat_bnds[0], lat_bnds[1]) 
                long = np.random.uniform(long_bnds[0],long_bnds[1]) 
            else:
                r = 0.0001
                lat = np.random.uniform(lat - lat * r, lat + lat * r) 
                long = np.random.uniform(long - long * r, long + long * r) 
            photolocation = add_photolocation(PhotoLocation(**{'_id':str(ObjectId()), 'image_filename': filename, "point": GeoJSONPoint(**{'coordinates': [long, lat]})})) 
            report = add_location_to_report(report, photolocation)
            print("\n\ndone", added)
            report_len += 1
            # exit()
        # if np.random.rand() > 0.1:
        #     train_labels += f"{filename} {label}\n"
        # else:
        #     validation_labels += f"{filename} {label}\n"
    # label_to_content[str(label)] = dir
    # label += 1

