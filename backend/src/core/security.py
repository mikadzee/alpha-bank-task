from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from pwdlib import PasswordHash


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "local-only-change-this-secret-before-deployment")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "30"))
REFRESH_COOKIE_NAME = "refreshToken"
REFRESH_COOKIE_PATH = "/api/v1/auth"
password_hash = PasswordHash.recommended()


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user_id: UUID | str, role: str, session_id: UUID | str) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    token = jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "sid": str(session_id),
            "type": "access",
            "iat": now,
            "exp": expires_at,
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    return token, expires_at


def create_refresh_token(user_id: UUID | str, role: str, session_id: UUID | str) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=REFRESH_TOKEN_DAYS)
    token = jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "sid": str(session_id),
            "type": "refresh",
            "iat": now,
            "exp": expires_at,
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    return token, expires_at


def decode_token(token: str, verify_exp: bool = True) -> dict[str, Any]:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"verify_exp": verify_exp},
    )
