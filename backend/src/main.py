from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.src.api.routers import applications, auth, companies, documents, feed, products
from backend.src.api.routers import staff
from backend.src.core.security import password_hash
from backend.src.db import get_connection, init_db

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("creditory")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    ensure_demo_employee()
    ensure_demo_client()
    Path(os.getenv("UPLOADS_DIRECTORY", "/app/backend/uploads")).mkdir(parents=True, exist_ok=True)
    yield


def ensure_demo_employee() -> None:
    email = os.getenv("DEMO_EMPLOYEE_EMAIL", "").strip().lower()
    password = os.getenv("DEMO_EMPLOYEE_PASSWORD", "")
    if not email or not password:
        return
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT role FROM users WHERE email = %s", (email,))
        existing = cur.fetchone()
        if existing:
            if existing["role"] != "employee":
                raise RuntimeError("DEMO_EMPLOYEE_EMAIL already belongs to a non-employee account")
            return
        cur.execute(
            """INSERT INTO users (email, password_hash, role)
               VALUES (%s, %s, 'employee') ON CONFLICT (email) DO NOTHING""",
            (email, password_hash.hash(password)),
        )


def ensure_demo_client() -> None:
    if os.getenv("ENABLE_DEMO_ACCOUNTS", "false").lower() not in {"1", "true", "yes"}:
        return
    email = os.getenv("DEMO_CLIENT_EMAIL", "demo@creditory.local").strip().lower()
    password = os.getenv("DEMO_CLIENT_PASSWORD", "ClientDemo2026!")
    if not email or not password:
        return
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, role FROM users WHERE email = %s", (email,))
        existing = cur.fetchone()
        if existing and existing["role"] != "client":
            raise RuntimeError("DEMO_CLIENT_EMAIL already belongs to a non-client account")
        if existing:
            user_id = existing["id"]
        else:
            cur.execute(
                """INSERT INTO users (email, password_hash, role)
                   VALUES (%s, %s, 'client') RETURNING id""",
                (email, password_hash.hash(password)),
            )
            user_id = cur.fetchone()["id"]
        cur.execute(
            """INSERT INTO client_companies (user_id, inn, ogrn, company_name, address, okved)
               VALUES (%s, '7701234567', '1237700123456', 'ООО Демо ТехноПлюс',
                       'г. Москва, ул. Примерная, д. 10', '28.99')
               ON CONFLICT (user_id, inn) DO NOTHING""",
            (user_id,),
        )


app = FastAPI(
    title="Умный кредитный кабинет предпринимателя",
    description="Локальный MVP кредитного конвейера с синтетическими данными.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    fields: dict[str, str] = {}
    for error in exc.errors():
        path = ".".join(str(part) for part in error.get("loc", ()) if part not in {"body", "query", "path", "header"})
        if path:
            fields[path] = error.get("msg", "Некорректное значение")
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Проверьте обязательные поля", "fields": fields}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        body = {"error": {"code": detail.get("code", "HTTP_ERROR"), "message": detail.get("message", "Ошибка запроса"), "fields": detail.get("fields", {})}}
    else:
        body = {"error": {"code": "HTTP_ERROR", "message": str(detail), "fields": {}}}
    return JSONResponse(status_code=exc.status_code, content=body, headers=exc.headers)


@app.exception_handler(Exception)
async def internal_error_handler(_: Request, exc: Exception):
    logger.exception("Unhandled request error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "Внутренняя ошибка сервера", "fields": {}}},
    )


@app.get("/healthz", tags=["system"])
def healthz():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["applications"])
app.include_router(documents.router, prefix="/api/v1/applications", tags=["documents"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(feed.router, prefix="/api/v1/feed", tags=["feed"])
app.include_router(staff.router, prefix="/api/v1/staff", tags=["staff"])
