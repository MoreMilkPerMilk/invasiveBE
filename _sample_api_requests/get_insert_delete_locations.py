# Install the Python Requests library:
# `pip install requests`

import requests


def send_request():
    # /locations
    # GET http://localhost:8000/locations

    try:
        response = requests.get(
            url="http://localhost:8000/locations",
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


# Install the Python Requests library:
# `pip install requests`

import requests
import json


def send_request():
    # insert 180 Swann
    # POST http://localhost:8000/locations/add

    try:
        response = requests.post(
            url="http://localhost:8000/locations/add",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "name": "180 Swann Road Queensland"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


# Install the Python Requests library:
# `pip install requests`

import requests
import json


def send_request():
    # delete 180 Swann
    # POST http://localhost:8000/locations/delete

    try:
        response = requests.post(
            url="http://localhost:8000/locations/delete",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "name": "180 Swann Road Queensland"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


# Install the Python Requests library:
# `pip install requests`

import requests
import json


def send_request():
    # insert 134 Gailey
    # POST http://localhost:8000/locations/add

    try:
        response = requests.post(
            url="http://localhost:8000/locations/add",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "name": "134 Gailey Road Queensland"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


# Install the Python Requests library:
# `pip install requests`

import requests
import json


def send_request():
    # delete 134 Gailey
    # POST http://localhost:8000/locations/delete

    try:
        response = requests.post(
            url="http://localhost:8000/locations/delete",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "name": "134 Gailey Road Queensland"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


# Install the Python Requests library:
# `pip install requests`

import requests
import json


def send_request():
    # insert 180 Swann with weed 1
    # POST http://localhost:8000/locations/add

    try:
        response = requests.post(
            url="http://localhost:8000/locations/add",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "name": "180 Swann Road Queensland",
                "weeds_present": [
                    {
                        "species_id": 1,
                        "discovery_date": "2000-01-01",
                        "removed": True,
                        "replaced": True,
                        "replaced_species": "Sunflower",
                        "removal_date": "2000-01-02"
                    }
                ]
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


# Install the Python Requests library:
# `pip install requests`

import requests
import json


def send_request():
    # insert 180 Swann with weed 2
    # POST http://localhost:8000/locations/add

    try:
        response = requests.post(
            url="http://localhost:8000/locations/add",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "name": "180 Swann Road Queensland",
                "weeds_present": [
                    {
                        "species_id": 2,
                        "discovery_date": "2000-01-01",
                        "removed": True,
                        "replaced": True,
                        "replaced_species": "Sunflower",
                        "removal_date": "2000-01-02"
                    }
                ]
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


# Install the Python Requests library:
# `pip install requests`

import requests
import json


def send_request():
    # insert 180 Swann with weed 3, 4
    # POST http://localhost:8000/locations/add

    try:
        response = requests.post(
            url="http://localhost:8000/locations/add",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({
                "name": "180 Swann Road Queensland",
                "weeds_present": [
                    {
                        "species_id": 3,
                        "discovery_date": "2000-01-01",
                        "removed": True,
                        "replaced": True,
                        "replaced_species": "Sunflower",
                        "removal_date": "2000-01-02"
                    },
                    {
                        "species_id": 4,
                        "discovery_date": "2000-01-01",
                        "removed": True,
                        "replaced": True,
                        "replaced_species": "Sunflower",
                        "removal_date": "2000-01-02"
                    }
                ]
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


