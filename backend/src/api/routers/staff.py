from __future__ import annotations

import re
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from psycopg.types.json import Jsonb

from backend.src.api.dependencies import require_employee
from backend.src.api.schemas import StaffDecisionRequest
from backend.src.db import get_connection
from backend.src.services.recommendations import resolve_product

router = APIRouter()
REVIEWABLE_STATUSES = {"pending", "needs_info"}
VALID_FILTERS = {"pending", "needs_info", "approved", "rejected", "offer_made", "offer_accepted", "offer_declined", "all"}


def _not_found():
    raise HTTPException(status_code=404, detail={"code": "APPLICATION_NOT_FOUND", "message": "Заявка не найдена"})


@router.get("/applications")
def list_staff_applications(
    status: str = Query(default="pending"),
    search: str = Query(default="", max_length=120),
    _: dict = Depends(require_employee),
):
    if status not in VALID_FILTERS:
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "Неизвестный статус"})

    conditions = ["a.status <> 'draft'"]
    params: list = []
    if status != "all":
        conditions.append("a.status = %s")
        params.append(status)
    if search.strip():
        conditions.append("(a.company_data->>'companyName' ILIKE %s OR a.company_data->>'inn' ILIKE %s OR u.email ILIKE %s)")
        pattern = f"%{search.strip()}%"
        params.extend([pattern, pattern, pattern])

    query = f"""SELECT a.id, a.status, a.company_data, a.financial_data,
                       a.selected_product_id, a.submitted_at, a.created_at, a.updated_at,
                       u.email AS client_email, p.name AS product_name
                FROM applications a
                JOIN users u ON u.id = a.user_id
                LEFT JOIN loan_products p ON p.id = a.selected_product_id
                WHERE {' AND '.join(conditions)}
                ORDER BY CASE a.status WHEN 'pending' THEN 0 WHEN 'needs_info' THEN 1 ELSE 2 END,
                         a.submitted_at DESC NULLS LAST, a.updated_at DESC"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    return [{
        "id": str(row["id"]),
        "status": row["status"],
        "companyData": row["company_data"],
        "financialData": row["financial_data"],
        "selectedProductId": str(row["selected_product_id"]) if row["selected_product_id"] else None,
        "productName": row["product_name"],
        "clientEmail": row["client_email"],
        "submittedAt": row["submitted_at"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    } for row in rows]


@router.get("/applications/{application_id}")
def get_staff_application(application_id: UUID, _: dict = Depends(require_employee)):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT a.*, u.email AS client_email, p.name AS product_name
               FROM applications a
               JOIN users u ON u.id = a.user_id
               LEFT JOIN loan_products p ON p.id = a.selected_product_id
               WHERE a.id = %s AND a.status <> 'draft'""",
            (application_id,),
        )
        row = cur.fetchone()
        if row is None:
            _not_found()
        cur.execute(
            """SELECT id, document_type, original_name, mime_type, size_bytes, uploaded_at
               FROM documents WHERE application_id = %s ORDER BY uploaded_at, id""",
            (application_id,),
        )
        documents = cur.fetchall()
        cur.execute(
            """SELECT id, event_type, from_status, to_status, note, created_at
               FROM application_events WHERE application_id = %s ORDER BY created_at, id""",
            (application_id,),
        )
        events = cur.fetchall()

    financial = row["financial_data"] or {}
    offer = None
    # The selected product is recalculated from the same catalog used at submission.
    with get_connection() as conn, conn.cursor() as cur:
        if row["selected_product_id"]:
            offer = resolve_product(cur, str(row["selected_product_id"]), financial)
    revenue = int(financial.get("annualRevenue") or 0)
    expenses = int(financial.get("monthlyExpenses") or 0)
    cash_flow = revenue // 12 - expenses
    payment = int((offer or {}).get("monthlyPayment") or 0)
    coverage = cash_flow / payment if payment else 0
    return {
        "id": str(row["id"]),
        "status": row["status"],
        "companyData": row["company_data"],
        "financialData": financial,
        "selectedProductId": str(row["selected_product_id"]) if row["selected_product_id"] else None,
        "productName": row["product_name"],
        "clientEmail": row["client_email"],
        "submittedAt": row["submitted_at"],
        "createdAt": row["created_at"],
        "reviewComment": row["review_comment"],
        "reviewedAt": row["reviewed_at"],
        "documents": [{
            "id": str(document["id"]),
            "type": document["document_type"],
            "originalName": document["original_name"],
            "mimeType": document["mime_type"],
            "sizeBytes": document["size_bytes"],
            "uploadedAt": document["uploaded_at"],
        } for document in documents],
        "offerData": row.get("offer_data"),
        "events": [{
            "id": str(event["id"]),
            "type": event["event_type"],
            "fromStatus": event["from_status"],
            "toStatus": event["to_status"],
            "note": event["note"],
            "createdAt": event["created_at"],
        } for event in events],
        "assessment": {
            "monthlyFreeCashFlow": cash_flow,
            "monthlyPayment": payment,
            "paymentCoverage": round(coverage, 2),
            "riskLevel": "high" if coverage < 1 else "medium" if coverage < 1.5 else "standard",
            "note": "Демонстрационная оценка по введённым доходам и расходам; это не банковский скоринг.",
            "factors": [
                {"label": "Выручка в месяц (среднее)", "value": revenue // 12, "effect": "input"},
                {"label": "Расходы в месяц", "value": expenses, "effect": "input"},
                {"label": "Свободный поток до кредита", "value": cash_flow, "effect": "warning" if cash_flow <= 0 else "positive"},
                {"label": "Платёж по выбранному продукту", "value": payment, "effect": "warning" if payment > cash_flow else "neutral"},
                {"label": "Покрытие платежа потоком", "value": round(coverage, 2), "effect": "warning" if coverage < 1 else "positive" if coverage >= 1.5 else "neutral"},
                {"label": "Загружено документов", "value": len(documents), "effect": "input"},
            ],
        },
    }


@router.get("/applications/{application_id}/documents/{document_id}")
def download_staff_document(
    application_id: UUID,
    document_id: UUID,
    _: dict = Depends(require_employee),
):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT d.storage_path, d.original_name, d.mime_type
               FROM documents d JOIN applications a ON a.id = d.application_id
               WHERE d.id = %s AND d.application_id = %s AND a.status <> 'draft'""",
            (document_id, application_id),
        )
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND", "message": "Документ не найден"})
    path = Path(row["storage_path"])
    if not path.is_file():
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_FILE_NOT_FOUND", "message": "Файл не найден"})
    safe_name = re.sub(r"[^\w.() -]", "_", row["original_name"])
    return FileResponse(path, media_type=row["mime_type"], filename=safe_name)


@router.post("/applications/{application_id}/decision")
def decide_application(
    application_id: UUID,
    data: StaffDecisionRequest,
    current_user: dict = Depends(require_employee),
):
    comment = data.comment.strip()
    if data.decision in {"rejected", "needs_info", "counteroffer"} and not comment:
        raise HTTPException(
            status_code=422,
            detail={"code": "VALIDATION_ERROR", "message": "Добавьте пояснение к решению", "fields": {"comment": "Это поле обязательно"}},
        )
    offer_data = None
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT status, selected_product_id, financial_data FROM applications WHERE id = %s", (application_id,))
        row = cur.fetchone()
        if row is None or row["status"] == "draft":
            _not_found()
        if row["status"] not in REVIEWABLE_STATUSES:
            raise HTTPException(status_code=409, detail={"code": "APPLICATION_ALREADY_REVIEWED", "message": "По заявке уже принято решение"})
        next_status = data.decision
        if data.decision == "counteroffer":
            if not row["selected_product_id"] or data.proposed_amount is None or data.proposed_term_months is None:
                raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "Укажите сумму и срок встречного предложения", "fields": {"proposedAmount": "Укажите сумму", "proposedTermMonths": "Укажите срок"}})
            financial = row["financial_data"] or {}
            proposed_financial = {**financial, "requestedAmount": data.proposed_amount, "requestedTermMonths": data.proposed_term_months}
            offer = resolve_product(cur, str(row["selected_product_id"]), proposed_financial)
            if offer is None or offer["amount"] != data.proposed_amount or offer["termMonths"] != data.proposed_term_months:
                raise HTTPException(status_code=422, detail={"code": "OFFER_OUT_OF_RANGE", "message": "Сумма или срок вне условий продукта", "fields": {"proposedAmount": "Проверьте пределы продукта", "proposedTermMonths": "Проверьте срок продукта"}})
            offer_data = {
                "productId": offer["productId"],
                "productName": offer["name"],
                "amount": offer["amount"],
                "termMonths": offer["termMonths"],
                "annualRate": offer["annualRate"],
                "monthlyPayment": offer["monthlyPayment"],
                "totalPayment": offer["totalPayment"],
            }
            next_status = "offer_made"
        cur.execute(
            """UPDATE applications
               SET status = %s, review_comment = %s, reviewed_by = %s, offer_data = %s,
                   reviewed_at = NOW(), updated_at = NOW()
               WHERE id = %s AND status IN ('pending', 'needs_info')
               RETURNING id, status, review_comment, reviewed_at, offer_data""",
            (next_status, comment or None, UUID(current_user["id"]), Jsonb(offer_data) if offer_data else None, application_id),
        )
        updated = cur.fetchone()
        if updated is None:
            raise HTTPException(status_code=409, detail={"code": "APPLICATION_ALREADY_REVIEWED", "message": "По заявке уже принято решение"})
        cur.execute(
            """INSERT INTO application_events (application_id, actor_user_id, event_type, from_status, to_status, note)
               VALUES (%s, %s, 'decision', %s, %s, %s)""",
            (application_id, UUID(current_user["id"]), row["status"], next_status, comment or "Решение банка зафиксировано"),
        )
    return {
        "id": str(updated["id"]),
        "status": updated["status"],
        "reviewComment": updated["review_comment"],
        "reviewedAt": updated["reviewed_at"],
        "offerData": updated["offer_data"],
    }
