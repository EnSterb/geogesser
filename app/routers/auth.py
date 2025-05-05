import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, APIRouter, status, Body
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.email_verification import send_verification_email, create_temp_user, verify_token_and_register
from app.models import User, TempUsers
from app.schemas import UserCreate, Token, UserPublic, UserLogin
from app.utils import verify_password, hash_password

load_dotenv(".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


def user_exists(email: str, db: Session) -> bool:
    return db.query(User).filter(User.email == email).first() is not None


def register_user(nickname: str, email: str, password: str, db: Session):
    try:
        # Проверяем, не зарегистрирован ли уже email или nickname
        if user_exists(email, db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        if db.query(User).filter(User.nickname == nickname).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname already taken"
            )

        if len(password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")

        # Создаем временную запись
        hashed_password = hash_password(password)
        token = create_temp_user(nickname, email, hashed_password, db)

        # Отправляем письмо с подтверждением
        send_verification_email(email, token)

        return {"message": "Verification email sent. Please check your email."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/verify_email")
def verify_email(token: str, db: Session = Depends(get_db)):
    if verify_token_and_register(token, db):
        return {"message": "Email successfully verified and account created"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired token"
    )


@router.post('/register/', response_model=dict)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return register_user(
        user_data.nickname,
        user_data.email,
        user_data.password,
        db
    )


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


@router.post("/login")
def login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(
        data={"sub": str(user.id_user)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,  # Поставь True на проде с HTTPS
        samesite="lax"
    )
    return response

security = HTTPBearer()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise credentials_exception

    stmt = select(User).where(User.id_user==user_id)
    user = db.execute(stmt).scalar()
    if user is None:
        raise credentials_exception
    return user


@router.get("/me")
def read_profile(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    return {
        'email': current_user.email,
        'access_token': token
    }

templates = Jinja2Templates(directory="app/templates")

@router.get("/register_page")
async def register_page(request: Request):
    return templates.TemplateResponse("register_page.html", {"request": request, "title": "register page"})

def get_user_from_cookie(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        # print("❌ Нет токена в cookies")
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        return None

    stmt = select(User).where(User.id_user == user_id)
    user = db.execute(stmt).scalar()
    return user