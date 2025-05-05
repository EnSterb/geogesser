from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request, Depends
from app.routers.auth import get_user_from_cookie

router = APIRouter(
    tags=['Pages'],
    prefix='/pages',
)

async def redirect_if_not_authenticated(request: Request, db: Session, redirect_to: str = "/pages/template"):
    user = get_user_from_cookie(request, db)
    if user is None:
        return RedirectResponse(redirect_to, status_code=302)
    return user

templates = Jinja2Templates(directory="app/templates")
@router.get("/hub", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    user = await redirect_if_not_authenticated(request, db)
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("hub.html", {"request": request, "title": "Camera"})

@router.get("/map", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("map.html", {"request": request, "title": "MAP"})

@router.get("/menu", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request, "title": "test"})

@router.get("/single_game", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("single_game.html", {"request": request, "title": "test"})

@router.get("/template", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    return templates.TemplateResponse("template.html", {
        "request": request,
        "user": user
    })

@router.get("/sign-up", response_class=HTMLResponse)
async def signup(request: Request, db: Session = Depends(get_db)):
    user = await redirect_if_not_authenticated(request, db)
    if not isinstance(user, RedirectResponse):
        return RedirectResponse("/pages/template", status_code=302)
    return templates.TemplateResponse("sign-up.html", {"request": request})

