import logging
import uvicorn
import pusher
from fastapi import FastAPI, Response, status, File, UploadFile, Form, Depends
from fastapi.staticfiles import StaticFiles

from typing import *
from db.database import database

from config.settings import settings 

from routers import communities, councils, users, photolocations, species, events, reports

app = FastAPI()

log = logging.getLogger("backend-logger")

@app.on_event("startup")
async def startup():
    app.state.db = database().get_client()
    app.state.pusher_client = pusher.Pusher(
        app_id = settings.pusher['app_id'],
        key = settings.pusher['key'],
        secret = settings.pusher['secret'],
        cluster = settings.pusher['cluster'],
        ssl = True
    )

    # SETUP UNIQUE KEYS
    councils.set_unique_keys(app.state.db.data.councils)
    photolocations.set_unique_keys(app.state.db.data.locations)
    events.set_unique_keys(app.state.db.data.events)
    users.set_unique_keys(app.state.db.data.users)
    communities.set_unique_keys(app.state.db.data.communities)
    reports.set_unique_keys(app.state.db.data.events)

app.include_router(communities.router)
app.include_router(events.router)
app.include_router(reports.router)
app.include_router(councils.router)
app.include_router(photolocations.router)
app.include_router(users.router)
app.include_router(species.router)

app.mount("/files", StaticFiles(directory="files"), name="files")

if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=80, reload=True)
