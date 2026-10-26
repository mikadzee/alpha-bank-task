from __future__ import annotations

import os
import re
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.src.api.dependencies import require_client
from backend.src.db import get_connection

router = APIRouter()
MAX_FILE_SIZE = 10 * 1024 * 1024
DOCUMENT_TYPES = {"egrul_extract", "accounting_report", "tax_certificate", "bank_statement", "other"}
SIGNATURES = {
    ".pdf": (b"%PDF-", "application/pdf"),
    ".png": (b"\x89PNG\r\n\x1a\n", "image/png"),
    ".jpg": (b"\xff\xd8\xff", "image/jpeg"),
    ".jpeg": (b"\xff\xd8\xff", "image/jpeg"),
}


def _owned_draft(cur, application_id: UUID, user_id: UUID) -> None:
    cur.execute("SELECT status FROM applications WHERE id = %s AND user_id = %s", (application_id, user_id))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "APPLICATION_NOT_FOUND", "message": "Заявка не найдена"})
    if row["status"] not in {"draft", "needs_info"}:
        raise HTTPException(status_code=409, detail={"code": "APPLICATION_LOCKED", "message": "Документы отправленной заявки нельзя изменить"})


@router.post("/{application_id}/documents", status_code=201)
async def upload_document(
    application_id: UUID,
    document_type: str = Form(alias="documentType"),
    file: UploadFile = File(...),
    current_user: dict = Depends(require_client),
):
    if document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "Неизвестный тип документа", "fields": {"documentType": "Выберите тип из списка"}})
    original_name = Path(file.filename or "document").name
    extension = Path(original_name).suffix.lower()
    if extension not in SIGNATURES:
        raise HTTPException(status_code=422, detail={"code": "UNSUPPORTED_FILE", "message": "Можно загрузить PDF, JPG или PNG"})
    content = await file.read(MAX_FILE_SIZE + 1)
    if not content or len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail={"code": "FILE_TOO_LARGE", "message": "Файл должен быть не больше 10 МБ"})
    signature, mime_type = SIGNATURES[extension]
    if not content.startswith(signature):
        raise HTTPException(status_code=422, detail={"code": "INVALID_FILE", "message": "Формат файла не совпадает с содержимым"})

    directory = Path(os.getenv("UPLOADS_DIRECTORY", "/app/backend/uploads"))
    directory.mkdir(parents=True, exist_ok=True)
    document_id = uuid4()
    path = directory / f"{document_id}{extension}"
    path.write_bytes(content)
    try:
        with get_connection() as conn, conn.cursor() as cur:
            _owned_draft(cur, application_id, UUID(current_user["id"]))
            cur.execute(
                """INSERT INTO documents (id, application_id, document_type, original_name, storage_path, mime_type, size_bytes)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (document_id, application_id, document_type, original_name, str(path), mime_type, len(content)),
            )
        return {"documentId": str(document_id), "id": str(document_id), "type": document_type, "documentType": document_type, "originalName": original_name, "sizeBytes": len(content)}
    except Exception:
        path.unlink(missing_ok=True)
        raise


def _get_document(application_id: UUID, document_id: UUID, user: dict):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT d.* FROM documents d JOIN applications a ON a.id = d.application_id
               WHERE d.id = %s AND d.application_id = %s AND a.user_id = %s""",
            (document_id, application_id, UUID(user["id"])),
        )
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND", "message": "Документ не найден"})
    return row


@router.get("/{application_id}/documents/{document_id}")
def download_document(application_id: UUID, document_id: UUID, current_user: dict = Depends(require_client)):
    document = _get_document(application_id, document_id, current_user)
    path = Path(document["storage_path"])
    if not path.is_file():
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_FILE_NOT_FOUND", "message": "Файл не найден"})
    safe_name = re.sub(r"[^\w.() -]", "_", document["original_name"])
    return FileResponse(path, media_type=document["mime_type"], filename=safe_name)


@router.delete("/{application_id}/documents/{document_id}", status_code=204)
def delete_document(application_id: UUID, document_id: UUID, current_user: dict = Depends(require_client)):
    path = None
    with get_connection() as conn, conn.cursor() as cur:
        _owned_draft(cur, application_id, UUID(current_user["id"]))
        cur.execute("DELETE FROM documents WHERE id = %s AND application_id = %s RETURNING storage_path", (document_id, application_id))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND", "message": "Документ не найден"})
        path = Path(row["storage_path"])
    path.unlink(missing_ok=True)
