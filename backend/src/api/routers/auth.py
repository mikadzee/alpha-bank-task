from __future__ import annotations

import hmac
import os
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from jwt import InvalidTokenError
from psycopg.errors import UniqueViolation

from backend.src.api.dependencies import get_current_user
from backend.src.api.schemas import LoginRequest, RegisterRequest
from backend.src.core.security import (
    REFRESH_COOKIE_NAME,
    REFRESH_COOKIE_PATH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token,
    password_hash,
)
from backend.src.db import get_connection

router = APIRouter()


def _set_refresh_cookie(response: Response, token: str, expires_at: datetime) -> None:
    max_age = max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        token,
        httponly=True,
        secure=os.getenv("REFRESH_COOKIE_SECURE", "false").lower() == "true",
        samesite=os.getenv("REFRESH_COOKIE_SAMESITE", "lax"),
        path=REFRESH_COOKIE_PATH,
        max_age=max_age,
        expires=expires_at,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        secure=os.getenv("REFRESH_COOKIE_SECURE", "false").lower() == "true",
        samesite=os.getenv("REFRESH_COOKIE_SAMESITE", "lax"),
    )


def _issue_session(user: dict, response: Response) -> dict:
    session_id = uuid4()
    access_token, access_expires_at = create_access_token(user["id"], user["role"], session_id)
    refresh_token, refresh_expires_at = create_refresh_token(user["id"], user["role"], session_id)
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO auth_sessions (id, user_id, refresh_token_hash, expires_at) VALUES (%s, %s, %s, %s)",
            (session_id, user["id"], hash_refresh_token(refresh_token), refresh_expires_at),
        )
    _set_refresh_cookie(response, refresh_token, refresh_expires_at)
    return {
        "accessToken": access_token,
        "tokenType": "bearer",
        "expiresIn": max(0, int((access_expires_at - datetime.now(timezone.utc)).total_seconds())),
        "user": user,
    }


@router.post("/register", status_code=201)
def register(data: RegisterRequest, response: Response):
    email = str(data.email).strip().lower()
    if data.password != data.password_confirmation:
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "Пароли не совпадают", "fields": {"passwordConfirmation": "Пароли не совпадают"}})

    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'client') RETURNING id, email, role",
                (email, password_hash.hash(data.password)),
            )
            row = cur.fetchone()
            user = {"id": str(row["id"]), "email": row["email"], "role": row["role"]}
            session_id = uuid4()
            access_token, access_expiry = create_access_token(user["id"], user["role"], session_id)
            refresh_token, refresh_expiry = create_refresh_token(user["id"], user["role"], session_id)
            cur.execute(
                "INSERT INTO auth_sessions (id, user_id, refresh_token_hash, expires_at) VALUES (%s, %s, %s, %s)",
                (session_id, user["id"], hash_refresh_token(refresh_token), refresh_expiry),
            )
    except UniqueViolation:
        raise HTTPException(status_code=409, detail={"code": "EMAIL_EXISTS", "message": "Пользователь с такой почтой уже зарегистрирован", "fields": {"email": "Эта почта уже используется"}})

    _set_refresh_cookie(response, refresh_token, refresh_expiry)
    return {"accessToken": access_token, "tokenType": "bearer", "expiresIn": max(0, int((access_expiry - datetime.now(timezone.utc)).total_seconds())), "user": user}


@router.post("/login")
def login(data: LoginRequest, response: Response):
    email = str(data.email).strip().lower()
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, email, role, password_hash FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
    if row is None or not password_hash.verify(data.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Неверная почта или пароль"})
    user = {"id": str(row["id"]), "email": row["email"], "role": row["role"]}
    return _issue_session(user, response)


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/refresh")
def refresh(response: Response, refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME)):
    if not refresh_token:
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail={"code": "REFRESH_REQUIRED", "message": "Сессия истекла. Войдите снова"})
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("wrong token type")
        user_id, session_id = UUID(payload["sub"]), UUID(payload["sid"])
    except (InvalidTokenError, KeyError, TypeError, ValueError):
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=401, detail={"code": "REFRESH_INVALID", "message": "Сессия истекла. Войдите снова"})

    now = datetime.now(timezone.utc)
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT s.refresh_token_hash, s.expires_at, s.revoked_at, u.email, u.role
               FROM auth_sessions s JOIN users u ON u.id = s.user_id
               WHERE s.id = %s AND s.user_id = %s FOR UPDATE OF s""",
            (session_id, user_id),
        )
        session = cur.fetchone()
        if (
            session is None
            or session["revoked_at"] is not None
            or session["expires_at"] <= now
            or not hmac.compare_digest(session["refresh_token_hash"], hash_refresh_token(refresh_token))
        ):
            _clear_refresh_cookie(response)
            raise HTTPException(status_code=401, detail={"code": "REFRESH_INVALID", "message": "Сессия истекла. Войдите снова"})

        user = {"id": str(user_id), "email": session["email"], "role": session["role"]}
        access_token, access_expiry = create_access_token(user_id, user["role"], session_id)
        new_refresh_token, refresh_expiry = create_refresh_token(user_id, user["role"], session_id)
        cur.execute(
            "UPDATE auth_sessions SET refresh_token_hash = %s, expires_at = %s WHERE id = %s",
            (hash_refresh_token(new_refresh_token), refresh_expiry, session_id),
        )
    _set_refresh_cookie(response, new_refresh_token, refresh_expiry)
    return {"accessToken": access_token, "tokenType": "bearer", "expiresIn": max(0, int((access_expiry - datetime.now(timezone.utc)).total_seconds())), "user": user}


@router.post("/logout", status_code=204)
def logout(response: Response, refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME)):
    if refresh_token:
        try:
            payload = decode_token(refresh_token, verify_exp=False)
            if payload.get("type") == "refresh":
                user_id, session_id = UUID(payload["sub"]), UUID(payload["sid"])
                with get_connection() as conn, conn.cursor() as cur:
                    cur.execute(
                        "UPDATE auth_sessions SET revoked_at = NOW() WHERE id = %s AND user_id = %s AND revoked_at IS NULL",
                        (session_id, user_id),
                    )
        except (InvalidTokenError, KeyError, TypeError, ValueError):
            pass
    _clear_refresh_cookie(response)
    return response
