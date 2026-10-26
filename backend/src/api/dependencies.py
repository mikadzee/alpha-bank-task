from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from jwt import InvalidTokenError

from backend.src.core.security import decode_token
from backend.src.db import get_connection


def get_current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Требуется вход в аккаунт"})
    try:
        payload = decode_token(authorization.removeprefix("Bearer "))
        if payload.get("type") != "access":
            raise InvalidTokenError("wrong token type")
        user_id = UUID(payload["sub"])
        session_id = UUID(payload["sid"])
    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Сессия истекла. Войдите снова"})

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT u.id, u.email, u.role
               FROM users u JOIN auth_sessions s ON s.user_id = u.id
               WHERE u.id = %s AND s.id = %s AND s.revoked_at IS NULL AND s.expires_at > NOW()""",
            (user_id, session_id),
        )
        user = cur.fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Сессия больше не активна"})
    return {"id": str(user["id"]), "email": user["email"], "role": user["role"]}


def require_client(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "client":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Действие доступно клиенту"})
    return current_user


def require_employee(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Действие доступно сотруднику банка"})
    return current_user
