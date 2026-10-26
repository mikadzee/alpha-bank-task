from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from backend.src.api.dependencies import require_client
from backend.src.api.schemas import CompanySaveRequest
from backend.src.db import get_connection

router = APIRouter()


def _company_response(row: dict) -> dict:
    return {
        "id": str(row["id"]),
        "inn": row["inn"],
        "ogrn": row["ogrn"],
        "companyName": row["company_name"],
        "address": row["address"],
        "okved": row["okved"],
        "updatedAt": row["updated_at"],
    }


@router.get("")
def list_companies(current_user: dict = Depends(require_client)):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM client_companies WHERE user_id = %s ORDER BY updated_at DESC, company_name",
            (UUID(current_user["id"]),),
        )
        return [_company_response(row) for row in cur.fetchall()]


@router.post("", status_code=200)
def save_company(data: CompanySaveRequest, current_user: dict = Depends(require_client)):
    company_name = data.company_name.strip()
    okved = data.okved.strip()
    if not company_name or not okved:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Проверьте данные компании",
                "fields": {"companyName" if not company_name else "okved": "Заполните поле"},
            },
        )

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO client_companies (user_id, inn, ogrn, company_name, address, okved)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (user_id, inn) DO UPDATE SET
                   ogrn = EXCLUDED.ogrn,
                   company_name = EXCLUDED.company_name,
                   address = EXCLUDED.address,
                   okved = EXCLUDED.okved,
                   updated_at = NOW()
               RETURNING *""",
            (UUID(current_user["id"]), data.inn, data.ogrn, company_name, data.address.strip(), okved),
        )
        return _company_response(cur.fetchone())


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: UUID, current_user: dict = Depends(require_client)):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM client_companies WHERE id = %s AND user_id = %s RETURNING id",
            (company_id, UUID(current_user["id"])),
        )
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail={"code": "COMPANY_NOT_FOUND", "message": "Компания не найдена"})
    return Response(status_code=204)


@router.get("/lookup")
def lookup_company(inn: str = Query(min_length=10, max_length=12), _: dict = Depends(require_client)):
    if not inn.isdigit() or len(inn) not in (10, 12):
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "ИНН должен содержать 10 или 12 цифр", "fields": {"inn": "Укажите 10 или 12 цифр"}})
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT inn, company_name, ogrn, address, okved FROM mock_companies WHERE inn = %s",
            (inn,),
        )
        row = cur.fetchone()
    if row is None:
        return {"found": False, "company": None}
    return {
        "found": True,
        "company": {
            "inn": row["inn"],
            "companyName": row["company_name"],
            "ogrn": row["ogrn"] or "",
            "address": row["address"] or "",
            "okved": row["okved"] or "",
        },
    }
