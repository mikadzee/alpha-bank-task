from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from psycopg.types.json import Jsonb

from backend.src.api.dependencies import require_client
from backend.src.api.schemas import DraftUpdate, OfferDecisionRequest, SubmitRequest
from backend.src.db import get_connection
from backend.src.services.recommendations import build_recommendations, resolve_product

router = APIRouter()
INN_PATTERN = re.compile(r"^(\d{10}|\d{12})$")
OGRN_PATTERN = re.compile(r"^(\d{13}|\d{15})$")
COMPANY_FIELDS = {"inn", "ogrn", "companyName", "address", "okved"}
FINANCIAL_FIELDS = {
    "annualRevenue", "monthlyExpenses", "requestedAmount",
    "requestedTermMonths", "purpose", "purposeDetails",
}
PURPOSES = {"working_capital", "equipment", "business_expansion", "other"}
REQUIRED_DOCUMENTS = {"egrul_extract", "accounting_report", "tax_certificate"}


def _bad(fields: dict[str, str], message: str = "Проверьте данные заявки"):
    raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": message, "fields": fields})


def _validate_company(data: dict[str, Any], complete: bool = False) -> None:
    fields: dict[str, str] = {}
    for name in set(data) - COMPANY_FIELDS:
        fields[name] = "Неизвестное поле"

    inn = str(data.get("inn", "")).strip()
    ogrn = str(data.get("ogrn", "")).strip()
    if complete and not INN_PATTERN.fullmatch(inn):
        fields["inn"] = "ИНН должен содержать 10 или 12 цифр"
    if complete and ogrn and not OGRN_PATTERN.fullmatch(ogrn):
        fields["ogrn"] = "ОГРН/ОГРНИП должен содержать 13 или 15 цифр"

    if complete:
        for name in ("companyName", "okved"):
            if not str(data.get(name, "")).strip():
                fields[name] = "Заполните поле"
    for name in ("companyName", "address", "okved"):
        value = data.get(name)
        if value is not None and not isinstance(value, str):
            fields[name] = "Ожидается текст"
    if len(str(data.get("companyName", ""))) > 255:
        fields["companyName"] = "Название компании слишком длинное"
    if fields:
        _bad(fields, "Проверьте данные компании")


def _validate_financial(data: dict[str, Any], complete: bool = False) -> None:
    fields: dict[str, str] = {}
    for name in set(data) - FINANCIAL_FIELDS:
        fields[name] = "Неизвестное поле"

    for name in ("annualRevenue", "monthlyExpenses", "requestedAmount", "requestedTermMonths"):
        value = data.get(name)
        if value is None:
            if complete:
                fields[name] = "Заполните поле"
            continue
        if isinstance(value, bool) or not isinstance(value, int):
            fields[name] = "Введите целое число рублей"
        elif value < 0 or (name in ("requestedAmount", "requestedTermMonths") and value == 0):
            fields[name] = "Значение должно быть больше нуля" if name in ("requestedAmount", "requestedTermMonths") else "Значение не может быть отрицательным"
        elif name != "requestedTermMonths" and value > 10_000_000_000:
            fields[name] = "Сумма превышает допустимый лимит"
        elif name == "requestedTermMonths" and value > 120:
            fields[name] = "Срок не может превышать 120 месяцев"

    purpose = data.get("purpose")
    if complete and purpose not in PURPOSES:
        fields["purpose"] = "Выберите цель финансирования"
    elif purpose and purpose not in PURPOSES:
        fields["purpose"] = "Выберите цель из списка"
    details = data.get("purposeDetails")
    if details is not None and not isinstance(details, str):
        fields["purposeDetails"] = "Ожидается текст"
    elif len(details or "") > 2000:
        fields["purposeDetails"] = "Слишком длинное пояснение"
    if fields:
        _bad(fields, "Проверьте финансовые данные")


def _get_application(cur, application_id: UUID, user_id: UUID):
    cur.execute(
        "SELECT * FROM applications WHERE id = %s AND user_id = %s",
        (application_id, user_id),
    )
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "APPLICATION_NOT_FOUND", "message": "Заявка не найдена"})
    return row


def _application_response(cur, row: dict) -> dict:
    cur.execute(
        "SELECT id, document_type, original_name, size_bytes, uploaded_at FROM documents WHERE application_id = %s ORDER BY uploaded_at, id",
        (row["id"],),
    )
    documents = [{
        "documentId": str(item["id"]),
        "id": str(item["id"]),
        "type": item["document_type"],
        "documentType": item["document_type"],
        "originalName": item["original_name"],
        "sizeBytes": item["size_bytes"],
        "uploadedAt": item["uploaded_at"],
    } for item in cur.fetchall()]
    cur.execute(
        """SELECT id, event_type, from_status, to_status, note, created_at
           FROM application_events WHERE application_id = %s
           ORDER BY created_at, id""",
        (row["id"],),
    )
    events = [{
        "id": str(item["id"]),
        "type": item["event_type"],
        "fromStatus": item["from_status"],
        "toStatus": item["to_status"],
        "note": item["note"],
        "createdAt": item["created_at"],
    } for item in cur.fetchall()]
    return {
        "id": str(row["id"]),
        "status": row["status"],
        "companyData": row["company_data"],
        "financialData": row["financial_data"],
        "selectedProductId": row["selected_product_id"],
        "offerData": row.get("offer_data"),
        "submittedAt": row["submitted_at"],
        "reviewComment": row.get("review_comment"),
        "reviewedAt": row.get("reviewed_at"),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
        "documents": documents,
        "events": events,
    }


@router.post("", status_code=201)
def create_application(current_user: dict = Depends(require_client)):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO applications (user_id) VALUES (%s) RETURNING *", (UUID(current_user["id"]),))
        row = cur.fetchone()
        cur.execute(
            """INSERT INTO application_events (application_id, actor_user_id, event_type, to_status, note)
               VALUES (%s, %s, 'draft_created', 'draft', 'Черновик заявки создан')""",
            (row["id"], UUID(current_user["id"])),
        )
        return _application_response(cur, row)


@router.get("")
def list_applications(current_user: dict = Depends(require_client)):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM applications WHERE user_id = %s ORDER BY updated_at DESC", (UUID(current_user["id"]),))
        return [_application_response(cur, row) for row in cur.fetchall()]


@router.get("/{application_id}")
def get_application(application_id: UUID, current_user: dict = Depends(require_client)):
    with get_connection() as conn, conn.cursor() as cur:
        return _application_response(cur, _get_application(cur, application_id, UUID(current_user["id"])))


@router.patch("/{application_id}")
def update_application(application_id: UUID, data: DraftUpdate, current_user: dict = Depends(require_client)):
    changes = data.model_dump(exclude_unset=True)
    company = changes.get("company_data")
    financial = changes.get("financial_data")
    if not changes:
        _bad({}, "Не переданы данные для сохранения")
    if company is not None:
        _validate_company(company)
    if financial is not None:
        _validate_financial(financial)

    user_id = UUID(current_user["id"])
    with get_connection() as conn, conn.cursor() as cur:
        row = _get_application(cur, application_id, user_id)
        if row["status"] not in {"draft", "needs_info"}:
            raise HTTPException(status_code=409, detail={"code": "APPLICATION_LOCKED", "message": "Отправленную заявку нельзя изменить"})
        updated_company = {**(row["company_data"] or {}), **(company or {})}
        updated_financial = {**(row["financial_data"] or {}), **(financial or {})}
        cur.execute(
            """UPDATE applications SET company_data = %s, financial_data = %s, updated_at = NOW()
               WHERE id = %s AND user_id = %s AND status IN ('draft', 'needs_info') RETURNING *""",
            (Jsonb(updated_company), Jsonb(updated_financial), application_id, user_id),
        )
        updated = cur.fetchone()
        if row["status"] == "needs_info":
            cur.execute(
                """INSERT INTO application_events (application_id, actor_user_id, event_type, from_status, to_status, note)
                   VALUES (%s, %s, 'client_updated', 'needs_info', 'needs_info', 'Клиент обновил данные заявки')""",
                (application_id, user_id),
            )
        return _application_response(cur, updated)


@router.get("/{application_id}/recommendations")
def recommendations(application_id: UUID, current_user: dict = Depends(require_client)):
    with get_connection() as conn, conn.cursor() as cur:
        row = _get_application(cur, application_id, UUID(current_user["id"]))
        _validate_financial(row["financial_data"] or {}, complete=True)
        return build_recommendations(cur, row["financial_data"] or {})


@router.post("/{application_id}/submit")
def submit_application(application_id: UUID, data: SubmitRequest, current_user: dict = Depends(require_client)):
    user_id = UUID(current_user["id"])
    with get_connection() as conn, conn.cursor() as cur:
        row = _get_application(cur, application_id, user_id)
        if row["status"] not in {"draft", "needs_info"}:
            raise HTTPException(status_code=409, detail={"code": "APPLICATION_ALREADY_SUBMITTED", "message": "Заявка уже отправлена"})
        company = row["company_data"] or {}
        financial = row["financial_data"] or {}
        _validate_company(company, complete=True)
        _validate_financial(financial, complete=True)

        cur.execute("SELECT DISTINCT document_type FROM documents WHERE application_id = %s", (application_id,))
        uploaded = {item["document_type"] for item in cur.fetchall()}
        missing = sorted(REQUIRED_DOCUMENTS - uploaded)
        if missing:
            _bad({name: "Загрузите обязательный документ" for name in missing}, "Не загружены обязательные документы")

        offer = resolve_product(cur, data.product_id, financial)
        if offer is None:
            _bad({"productId": "Выберите подходящее предложение из списка"}, "Кредитное предложение недоступно")
        cur.execute(
            """UPDATE applications SET selected_product_id = %s, status = 'pending', submitted_at = NOW(),
                       review_comment = NULL, reviewed_by = NULL, reviewed_at = NULL, offer_data = NULL, updated_at = NOW()
               WHERE id = %s AND user_id = %s AND status IN ('draft', 'needs_info') RETURNING *""",
            (UUID(offer["productId"]), application_id, user_id),
        )
        updated = cur.fetchone()
        if updated is None:
            raise HTTPException(status_code=409, detail={"code": "APPLICATION_ALREADY_SUBMITTED", "message": "Заявка уже отправлена"})
        event_type = "resubmitted" if row["status"] == "needs_info" else "submitted"
        event_note = "Исправленная заявка повторно отправлена" if row["status"] == "needs_info" else "Заявка отправлена в банк"
        cur.execute(
            """INSERT INTO application_events (application_id, actor_user_id, event_type, from_status, to_status, note)
               VALUES (%s, %s, %s, %s, 'pending', %s)""",
            (application_id, user_id, event_type, row["status"], event_note),
        )
        return _application_response(cur, updated)


@router.post("/{application_id}/offer-decision")
def decide_offer(application_id: UUID, data: OfferDecisionRequest, current_user: dict = Depends(require_client)):
    user_id = UUID(current_user["id"])
    next_status = "offer_accepted" if data.decision == "accept" else "offer_declined"
    note = "Клиент принял предложенные условия" if data.decision == "accept" else "Клиент отклонил предложенные условия"
    with get_connection() as conn, conn.cursor() as cur:
        row = _get_application(cur, application_id, user_id)
        if row["status"] != "offer_made":
            raise HTTPException(status_code=409, detail={"code": "OFFER_NOT_AVAILABLE", "message": "По заявке нет ожидающего предложения банка"})
        cur.execute(
            """UPDATE applications SET status = %s, updated_at = NOW()
               WHERE id = %s AND user_id = %s AND status = 'offer_made' RETURNING *""",
            (next_status, application_id, user_id),
        )
        updated = cur.fetchone()
        cur.execute(
            """INSERT INTO application_events (application_id, actor_user_id, event_type, from_status, to_status, note)
               VALUES (%s, %s, %s, 'offer_made', %s, %s)""",
            (application_id, user_id, data.decision, next_status, note),
        )
        return _application_response(cur, updated)
