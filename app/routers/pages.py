from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user
from sqlalchemy.testing import db

from app.database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request, Depends

from app.models import User, GameRoom, SoloRoom, SoloRound
from app.routers.auth import get_user_from_cookie

router = APIRouter(
    tags=['Pages'],
    prefix='/pages',
)

async def redirect_if_not_authenticated(request: Request, db: Session, redirect_to: str = "/pages/sign-in"):
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
    return templates.TemplateResponse("hub.html", {
        "request": request,
        "user": user
    })

@router.get("/map", response_class=HTMLResponse)
async def read_root(request: Request):
    user = await redirect_if_not_authenticated(request, db)
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("map.html", {
        "request": request,
        "user": user,
    })

@router.get("/menu", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    user = await redirect_if_not_authenticated(request, db)
    if isinstance(user, RedirectResponse):
        return templates.TemplateResponse("menu.html", {
        "request": request
    })
    return templates.TemplateResponse("menu.html", {
        "request": request,
        "user": user
    })

@router.get("/single-game", response_class=HTMLResponse)
async   def single_player_page(request: Request, db: Session = Depends(get_db)):
    user = await redirect_if_not_authenticated(request, db)
    if isinstance(user, RedirectResponse):
        return user
    user_rooms = []
    if user:
        user_rooms = db.query(SoloRoom).filter(SoloRoom.id_user == user.id_user).order_by(
            SoloRoom.created_at.desc()).all()
    # print(user.id_user, user_rooms)
    return templates.TemplateResponse("single-game.html", {
        "request": request,
        "rooms": user_rooms,
        "user": user
    })

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
        return templates.TemplateResponse("menu.html", {
        "request": request,
        "user": user
    })
    return templates.TemplateResponse("sign-up.html", {"request": request})

@router.get("/email-sent", response_class=HTMLResponse)
async def email_sent_page(request: Request, db:Session = Depends(get_db)):
    user = await redirect_if_not_authenticated(request, db)
    if not isinstance(user, RedirectResponse):
        return templates.TemplateResponse("menu.html", {
            "request": request,
            "user": user
        })
    return templates.TemplateResponse("email-sent.html", {"request": request})

@router.get("/sign-in", response_class=HTMLResponse)
async def signup(request: Request, db: Session = Depends(get_db)):
    user = await redirect_if_not_authenticated(request, db)
    if not isinstance(user, RedirectResponse):
        return templates.TemplateResponse("menu.html", {
            "request": request,
            "user": user
        })
    return templates.TemplateResponse("sign-in.html", {"request": request})

@router.get("/single-room/{room_id}", response_model=None)
def show_room_page(
    room_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_user_from_cookie(request, db)
    if current_user is None:
        return RedirectResponse("/pages/sign-in", status_code=302)
    room = db.query(SoloRoom).filter(SoloRoom.id_solo_room == room_id, SoloRoom.id_user == current_user.id_user).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    rounds = db.query(SoloRound).filter(SoloRound.id_solo_room == room.id_solo_room).all()

    return templates.TemplateResponse("room-page.html", {
        "request": request,
        "room": room,
        "rounds": rounds,
        "user": current_user
    })
