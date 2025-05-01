import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import TempUsers, User
from .database import get_db
from .send_email import send_email
import os


def create_temp_user(
    nickname: str,
    email: str,
    password_hash: str,
    db: Session
) -> str:
    try:
        # Удаляем старые записи для этого email
        db.execute(
            delete(TempUsers)
            .where(TempUsers.email == email)
        )

        # Создаем новую временную запись
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=30)

        temp_user = TempUsers(
            nickname=nickname,
            email=email,
            password_hash=password_hash,
            token=token,
            expires_at=expires_at
        )

        db.add(temp_user)
        db.commit()

        return token
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def send_verification_email(email: str, token: str):
    verification_url = f"{os.getenv('BASE_URL')}/auth/verify_email?token={token}"

    subject = "Подтверждение регистрации"
    body = f"""
    Добро пожаловать!
    Пожалуйста, подтвердите ваш email, перейдя по ссылке:
    {verification_url}

    Ссылка действительна 30 минут.
    """

    send_email(
        email_from=os.getenv("GMAIL"),
        email_password=os.getenv("GMAILPASSWORD"),
        email_to=email,
        subject=subject,
        body=body
    )


def verify_token_and_register(token: str, db: Session) -> bool:
    try:
        # Находим временного пользователя
        temp_user = db.query(TempUsers).filter(
            TempUsers.token == token,
            TempUsers.expires_at > datetime.utcnow()
        ).first()

        if not temp_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expired"
            )

        # Проверяем, не зарегистрирован ли уже email или nickname
        existing_user = db.query(User).filter(
            (User.email == temp_user.email) |
            (User.nickname == temp_user.nickname)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or nickname already registered"
            )

        # Создаем настоящего пользователя
        new_user = User(
            nickname=temp_user.nickname,
            email=temp_user.email,
            hashed_password=temp_user.password_hash
        )

        db.add(new_user)
        db.delete(temp_user)  # Удаляем временную запись
        db.commit()

        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )