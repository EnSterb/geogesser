from sys import prefix

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.openapi.utils import get_openapi

from app.models import Location
from app.schemas import LocationPublic
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
from app.routers.game import router as game_router
from app.database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request, Depends
from fastapi.responses import FileResponse
from app.routers.auth import router as auth_router

app = FastAPI(
    prefix='geogesser',
    title='Geogesser',
    version='0.1.1',
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        routes=app.routes,
    )

    # Добавляем поддержку OAuth2 в Swagger
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {},
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.include_router(auth_router)
app.include_router(game_router)

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

@app.get("/menu", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request, "title": "test"})

@app.get("/single_game", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("single_game.html", {"request": request, "title": "test"})