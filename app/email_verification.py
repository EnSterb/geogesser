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
        db.execute(
            delete(TempUsers)
            .where(TempUsers.email == email)
        )

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

    subject = "Registration Confirmation"
    html_body = f"""
    <html>
        <body>
            <p>Welcome!</p>
            <p>Please confirm your email by clicking the link below:</p>
            <p><a href="{verification_url}">For confirm registration click here</a></p>
            <p>The link is valid for 30 minutes.</p>
        </body>
    </html>
    """

    send_email(
        email_from=os.getenv("GMAIL"),
        email_password=os.getenv("GMAILPASSWORD"),
        email_to=email,
        subject=subject,
        body=html_body,
        is_html=True
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