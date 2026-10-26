from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any


def _money(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _format_money(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _payment(amount: int, months: int, annual_rate: Decimal) -> tuple[int, int]:
    principal = Decimal(amount)
    monthly_rate = annual_rate / Decimal("1200")
    if monthly_rate == 0:
        exact_payment = principal / months
    else:
        factor = (Decimal("1") + monthly_rate) ** months
        exact_payment = principal * monthly_rate * factor / (factor - Decimal("1"))
    return _money(exact_payment), _money(exact_payment * months)


def build_recommendations(cur, financial_data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    cur.execute(
        """SELECT id, code, name, purpose, description, min_amount, max_amount,
                  min_term_months, max_term_months, annual_rate
           FROM loan_products WHERE is_active = TRUE ORDER BY name"""
    )
    products = cur.fetchall()
    requested_amount = int(financial_data.get("requestedAmount") or 0)
    requested_term = int(financial_data.get("requestedTermMonths") or 0)
    revenue = int(financial_data.get("annualRevenue") or 0)
    expenses = int(financial_data.get("monthlyExpenses") or 0)
    purpose = financial_data.get("purpose")
    free_cash_flow = Decimal(revenue) / Decimal("12") - Decimal(expenses)
    offers: list[dict[str, Any]] = []

    for product in products:
        if purpose and product["purpose"] != purpose and product["purpose"] != "other":
            continue
        amount = max(int(product["min_amount"]), min(requested_amount or int(product["min_amount"]), int(product["max_amount"])))
        term = max(int(product["min_term_months"]), min(requested_term or int(product["min_term_months"]), int(product["max_term_months"])))
        rate = Decimal(product["annual_rate"])
        monthly_payment, total_payment = _payment(amount, term, rate)
        coverage = free_cash_flow / Decimal(monthly_payment) if monthly_payment else Decimal("0")
        recommended = coverage >= Decimal("1.5")
        warnings: list[str] = []
        if coverage < Decimal("1.5"):
            warnings.append(
                f"Свободный денежный поток составляет {_format_money(max(0, _money(free_cash_flow)))} ₽ в месяц. "
                "Платёж может заметно повлиять на бюджет компании."
            )
        if coverage < Decimal("1"):
            warnings.append("По указанным доходам и расходам свободного потока может не хватить на ежемесячный платёж.")

        reasons = [
            {
                "title": "Соответствует вашей цели",
                "description": product["description"],
            },
            {
                "title": "Платёж учитывает ваш денежный поток",
                "description": (
                    f"После расходов остаётся около {_format_money(max(0, _money(free_cash_flow)))} ₽ в месяц. "
                    f"Это примерно {max(0, coverage):.1f} ежемесячного платежа."
                    if free_cash_flow > 0
                    else "Укажите выручку и расходы, чтобы точнее оценить нагрузку на бюджет компании."
                ),
            },
            {
                "title": "Срок соответствует условиям продукта",
                "description": (
                    f"Можно выбрать от {product['min_term_months']} до {product['max_term_months']} месяцев. "
                    f"В расчёте использован срок {term} месяцев."
                ),
            },
        ]

        if requested_amount and requested_amount != amount:
            warnings.append(
                f"Сумма скорректирована до {_format_money(amount)} ₽ в пределах условий продукта "
                f"({_format_money(int(product['min_amount']))}–{_format_money(int(product['max_amount']))} ₽)."
            )

        offers.append({
            "productId": str(product["id"]),
            "code": product["code"],
            "name": product["name"],
            "description": product["description"],
            "amount": amount,
            "termMonths": term,
            "annualRate": float(rate),
            "monthlyPayment": monthly_payment,
            "totalPayment": total_payment,
            "recommended": recommended,
            "reasons": reasons,
            "warnings": warnings,
        })

    offers.sort(key=lambda item: (not item["recommended"], item["annualRate"], item["monthlyPayment"]))
    return {"recommendations": offers}


def resolve_product(cur, product_id: str, financial_data: dict[str, Any]) -> dict[str, Any] | None:
    offers = build_recommendations(cur, financial_data)["recommendations"]
    return next((offer for offer in offers if offer["productId"] == str(product_id) or offer["code"] == product_id), None)
