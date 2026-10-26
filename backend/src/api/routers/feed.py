from uuid import UUID

from fastapi import APIRouter, Depends

from backend.src.api.dependencies import require_client
from backend.src.db import get_connection

router = APIRouter()

SECTOR_TIPS = {
    "28.99": ("Промышленное оборудование", "Сравните график платежей с сезонностью заказов и сроками оплаты от покупателей."),
    "46.90": ("Оптовая торговля", "При расчёте оборотного финансирования учитывайте сроки оплаты поставщикам и дебиторскую задолженность."),
    "82.99": ("Услуги для бизнеса", "Проверьте, совпадает ли срок кредита с периодом, за который окупятся новые услуги или проекты."),
    "49.41": ("Логистика", "При планировании платежа учтите сезонные колебания загрузки транспорта и стоимость топлива."),
    "01.11": ("Сельское хозяйство", "Сопоставьте даты платежей с сезонным циклом работ и поступлением выручки."),
    "47.91": ("Розничная торговля", "Оцените сезонность продаж и запас денежных средств перед пиковыми периодами закупок."),
}


@router.get("")
def business_feed(current_user: dict = Depends(require_client)):
    """A small personalized demo feed derived only from the signed-in user's records."""
    user_id = UUID(current_user["id"])
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT company_name, inn, okved FROM client_companies
               WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1""",
            (user_id,),
        )
        company = cur.fetchone()
        cur.execute(
            """SELECT id, status, company_data, financial_data, review_comment, offer_data, updated_at
               FROM applications WHERE user_id = %s AND status <> 'draft'
               ORDER BY updated_at DESC LIMIT 1""",
            (user_id,),
        )
        application = cur.fetchone()

    feed = []
    if company:
        title, text = SECTOR_TIPS.get(
            company["okved"],
            ("Планирование финансирования", "Сравните предполагаемый платёж со свободным денежным потоком и сроком окупаемости цели."),
        )
        feed.append({"id": "sector-tip", "kind": "insight", "title": title, "description": text, "companyName": company["company_name"]})
    else:
        feed.append({"id": "company-tip", "kind": "next_step", "title": "Добавьте компанию", "description": "После заполнения реквизитов здесь появятся подсказки с учётом сферы вашего бизнеса."})

    if application:
        data = application["financial_data"] or {}
        annual_revenue = int(data.get("annualRevenue") or 0)
        monthly_expenses = int(data.get("monthlyExpenses") or 0)
        cash_flow = annual_revenue // 12 - monthly_expenses
        app_status = application["status"]
        labels = {"pending": "Заявка проверяется", "approved": "Заявка одобрена", "rejected": "По заявке получен отказ", "needs_info": "Нужно дополнить заявку", "offer_made": "Банк предложил другие условия", "offer_accepted": "Условия приняты", "offer_declined": "Предложение отклонено"}
        description = f"Свободный поток по введённым данным — около {cash_flow:,} ₽ в месяц.".replace(",", " ")
        if app_status == "needs_info" and application["review_comment"]:
            description += f" Комментарий банка: {application['review_comment']}"
        if app_status == "offer_made" and application["offer_data"]:
            proposed = application["offer_data"]
            description = f"Сумма {proposed['amount']:,} ₽ на {proposed['termMonths']} мес.; примерный платёж — {proposed['monthlyPayment']:,} ₽ в месяц.".replace(",", " ")
        feed.append({"id": f"application-{application['id']}", "kind": "application", "title": labels.get(app_status, "Обновление по заявке"), "description": description, "status": app_status})
    elif company:
        feed.append({"id": "finance-tip", "kind": "insight", "title": "Сначала — расчёт нагрузки", "description": "Для предварительной оценки укажите выручку, ежемесячные расходы, сумму и срок финансирования."})

    feed.append({"id": "demo-note", "kind": "notice", "title": "О демонстрационном кабинете", "description": "Подсказки и условия рассчитаны на синтетических данных. Проверки ФНС, БКИ и реальные банковские решения не подключены."})
    return {"items": feed}
