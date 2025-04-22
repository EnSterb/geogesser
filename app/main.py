from fastapi import FastAPI, HTTPException, Query, Depends
from app.models import Location
from app.schemas import LocationPublic
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
from app.sologame import router as sologame_router
from app.database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Depends
from fastapi.responses import FileResponse

app = FastAPI()
app.include_router(sologame_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")



@app.get("/db")
async def get_():
    db = get_db()
    return db

@app.get("/hub", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("hub.html", {"request": request, "title": "Camera"})

@app.get("/map", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("map.html", {"request": request, "title": "MAP"})