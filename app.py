import logging
import uvicorn
from fastapi import FastAPI, Response, status, File, UploadFile, Form, Depends

from typing import *
from db.database import database

import pusher.session

from routers import communities, councils, users, photolocations, species, events, reports

app = FastAPI()

log = logging.getLogger("backend-logger")

@app.on_event("startup")
async def startup():
    app.state.db = database().get_client()
    app.state.pusher_client = pusher.session().get_client()
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

if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8080, reload=True)
