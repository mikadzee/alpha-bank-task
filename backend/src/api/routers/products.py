from fastapi import APIRouter, Depends

from backend.src.api.dependencies import require_client
from backend.src.db import get_connection

router = APIRouter()


@router.get("")
def list_products(_: dict = Depends(require_client)):
    """Return the active demo catalogue; rates and limits are not bank offers."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT id, code, name, purpose, description, min_amount, max_amount,
                      min_term_months, max_term_months, annual_rate
               FROM loan_products WHERE is_active = TRUE ORDER BY name"""
        )
        rows = cur.fetchall()
    return [{
        "id": str(row["id"]),
        "code": row["code"],
        "name": row["name"],
        "purpose": row["purpose"],
        "description": row["description"],
        "minAmount": int(row["min_amount"]),
        "maxAmount": int(row["max_amount"]),
        "minTermMonths": row["min_term_months"],
        "maxTermMonths": row["max_term_months"],
        "annualRate": float(row["annual_rate"]),
    } for row in rows]
