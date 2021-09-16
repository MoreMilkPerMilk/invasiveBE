import logging
import uvicorn
from fastapi import FastAPI, Response, status, File, UploadFile, Form, Depends

from typing import *
from db.database import database

# 
# from Models.Person import Person
# from Models.WeedInstance import WeedInstance
# from Models.Location import Location
# from Models.Species import Species
# from Models.Council import Council
# from Models.GeoJSONPoint import GeoJSONPoint

from routers import communities, councils, persons, locations, species, weeds, events, reports
# from routers import councils
# from routers import persons
# from routers import locations 
# from routers import species 
# from routers import persons 
# from routers import weeds 
# from routers import events

app = FastAPI()

log = logging.getLogger("backend-logger")

@app.on_event("startup")
async def startup():
    app.state.db = database().get_client()

app.include_router(communities.router)
app.include_router(events.router)
app.include_router(reports.router)
app.include_router(councils.router)
app.include_router(locations.router)
app.include_router(persons.router)
app.include_router(species.router)
app.include_router(weeds.router)


# SETUP UNIQUE KEYS

councils.router.set_unique_keys(app.state.db.data.councils)
locations.router.set_unique_keys(app.state.db.data.locations)
weeds.router.set_unique_keys(app.state.db.data.weeds)
events.router.set_unique_keys(app.state.db.data.events)
persons.router.set_unique_keys(app.state.db.data.users)
communities.router.set_unique_keys(app.state.db.data.communities)
reports.router.set_unique_keys(app.state.db.data.events)

if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8080, reload=True)
