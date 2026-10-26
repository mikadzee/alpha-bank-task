<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import { useGlobalStore } from "~/stores";

definePageMeta({ layout: "default" });

const route = useRoute();
const store = useGlobalStore();
const id = String(route.params.id);
const loading = ref(true);
const saving = ref(false);
const error = ref("");
const comment = ref("");
const proposedAmount = ref(0);
const proposedTermMonths = ref(0);
const detail = computed(() => store.staffApplication);
const statusLabels: Record<string, string> = {
  pending: "На рассмотрении",
  needs_info: "Нужно уточнение",
  approved: "Одобрена",
  rejected: "Отклонена",
  offer_made: "Предложены другие условия",
  offer_accepted: "Условия приняты",
  offer_declined: "Предложение отклонено"
};

onMounted(async () => {
  try {
    await store.loadStaffApplication(id);
    comment.value = detail.value?.reviewComment || "";
    proposedAmount.value = Number(detail.value?.financialData?.requestedAmount || 0);
    proposedTermMonths.value = Number(detail.value?.financialData?.requestedTermMonths || 0);
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "Не удалось открыть заявку";
  } finally {
    loading.value = false;
  }
});

const money = (value?: number) => value == null ? "—" : `${new Intl.NumberFormat("ru-RU").format(value)} ₽`;
const date = (value?: string | null) => value
  ? new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value))
  : "—";
const purposeLabels: Record<string, string> = {
  working_capital: "Пополнение оборотных средств",
  equipment: "Покупка оборудования",
  business_expansion: "Развитие бизнеса",
  other: "Другая бизнес-цель"
};
const documentLabels: Record<string, string> = {
  egrul_extract: "Выписка из ЕГРЮЛ",
  accounting_report: "Бухгалтерская отчётность",
  tax_certificate: "Справка о налоговой задолженности",
  bank_statement: "Выписка по расчётному счёту",
  other: "Дополнительный документ"
};
const purposeLabel = (value?: string) => purposeLabels[value || ""] || value || "—";
const documentLabel = (value?: string) => documentLabels[value || ""] || value || "Документ";
const statusLabel = (value?: string) => statusLabels[value || ""] || "Заявка";
const canReview = computed(() => ["pending", "needs_info"].includes(detail.value?.status || ""));

async function downloadDocument(document: Record<string, any>) {
  if (!detail.value) return;
  error.value = "";
  try {
    const blob = await store.downloadStaffDocument(id, document.id);
    const url = URL.createObjectURL(blob);
    const link = window.document.createElement("a");
    link.href = url;
    link.download = document.originalName || "document";
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "Не удалось скачать документ";
  }
}

async function decide(decision: "approved" | "rejected" | "needs_info" | "counteroffer") {
  if (!detail.value) return;
  if (decision !== "approved" && !comment.value.trim()) {
    error.value = "Добавьте пояснение для клиента, чтобы отправить это решение.";
    return;
  }
  if (decision === "counteroffer" && (!Number.isInteger(proposedAmount.value) || proposedAmount.value <= 0 || !Number.isInteger(proposedTermMonths.value) || proposedTermMonths.value <= 0)) {
    error.value = "Укажите целую сумму и срок встречного предложения.";
    return;
  }
  saving.value = true;
  error.value = "";
  try {
    await store.decideStaffApplication(id, decision, comment.value.trim(), decision === "counteroffer" ? { proposedAmount: proposedAmount.value, proposedTermMonths: proposedTermMonths.value } : undefined);
    await navigateTo("/staff");
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "Не удалось сохранить решение";
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <section class="review-page">
    <NuxtLink class="back-link" to="/staff"><SvgIcon icon="icon-arrow-right" />К очереди заявок</NuxtLink>

    <div v-if="loading" class="review-loading"><span></span>Открываем заявку</div>
    <div v-else-if="!detail" class="review-error-page">
      <h1>Не удалось открыть заявку</h1>
      <p>{{ error || "Заявка не найдена или у вас нет доступа." }}</p>
    </div>
    <template v-else>
      <header class="review-heading">
        <div>
          <span class="eyebrow">Карточка заявки</span>
          <h1>{{ detail.companyData?.companyName || "Компания не указана" }}</h1>
          <p>ИНН {{ detail.companyData?.inn || "—" }} <span>·</span> {{ detail.clientEmail }}</p>
        </div>
        <span class="status" :class="detail.status">{{ statusLabel(detail.status) }}</span>
      </header>

      <p v-if="detail.reviewComment && detail.status === 'needs_info'" class="client-note">
        <b>Комментарий клиенту</b>{{ detail.reviewComment }}
      </p>
      <p v-if="error" class="feedback error">{{ error }}</p>

      <div class="review-grid">
        <div class="review-main">
          <section class="review-card">
            <div class="section-heading">
              <div><h2>Данные компании</h2><p>Информация из заявки клиента</p></div>
              <span class="section-icon"><SvgIcon icon="icon-building" /></span>
            </div>
            <div class="data-grid">
              <div class="data-field"><span>Название компании</span><b>{{ detail.companyData?.companyName || "—" }}</b></div>
              <div class="data-field"><span>ИНН</span><b>{{ detail.companyData?.inn || "—" }}</b></div>
              <div class="data-field"><span>ОГРН</span><b>{{ detail.companyData?.ogrn || "—" }}</b></div>
              <div class="data-field"><span>ОКВЭД</span><b>{{ detail.companyData?.okved || "—" }}</b></div>
              <div class="data-field full"><span>Адрес</span><b>{{ detail.companyData?.address || "—" }}</b></div>
            </div>
          </section>

          <section class="review-card">
            <div class="section-heading">
              <div><h2>Параметры финансирования</h2><p>{{ detail.productName || "Кредитное предложение" }}</p></div>
              <span class="section-icon"><SvgIcon icon="icon-credit-card" /></span>
            </div>
            <div class="data-grid financial-grid">
              <div class="data-field"><span>Запрашиваемая сумма</span><b>{{ money(detail.financialData?.requestedAmount) }}</b></div>
              <div class="data-field"><span>Срок</span><b>{{ detail.financialData?.requestedTermMonths || "—" }} мес.</b></div>
              <div class="data-field"><span>Годовая выручка</span><b>{{ money(detail.financialData?.annualRevenue) }}</b></div>
              <div class="data-field"><span>Расходы в месяц</span><b>{{ money(detail.financialData?.monthlyExpenses) }}</b></div>
              <div class="data-field full"><span>Цель</span><b>{{ detail.financialData?.purposeDetails || purposeLabel(detail.financialData?.purpose) }}</b></div>
            </div>
          </section>

          <section class="review-card">
            <div class="section-heading">
              <div><h2>Документы</h2><p>{{ detail.documents?.length || 0 }} файла приложено</p></div>
              <span class="section-icon"><SvgIcon icon="icon-folder" /></span>
            </div>
            <div v-if="detail.documents?.length" class="document-list">
              <div v-for="document in detail.documents" :key="document.id" class="document-row">
                <span class="file-icon"><SvgIcon icon="icon-file-text" /></span>
                <span class="file-info"><b>{{ document.originalName }}</b><small>{{ documentLabel(document.type) }} · {{ Math.max(1, Math.round(document.sizeBytes / 1024)) }} КБ</small></span>
                <button class="download" type="button" @click="downloadDocument(document)">Скачать</button>
              </div>
            </div>
            <div v-else class="documents-empty">К заявке пока не приложены документы.</div>
          </section>
        </div>

        <aside class="review-side">
          <section class="assessment-card">
            <span class="eyebrow">Предварительная проверка</span>
            <h2>Платёжная нагрузка</h2>
            <p class="assessment-note">{{ detail.assessment?.note }}</p>
            <div class="assessment-number">
              <span>Свободный поток в месяц</span>
              <b>{{ money(detail.assessment?.monthlyFreeCashFlow) }}</b>
            </div>
            <div class="assessment-number">
              <span>Ориентир платежа</span>
              <b>{{ money(detail.assessment?.monthlyPayment) }}</b>
            </div>
            <div class="coverage" :class="detail.assessment?.riskLevel">
              <span>Покрытие платежа</span>
              <b>{{ detail.assessment?.paymentCoverage }}×</b>
            </div>
            <div v-if="detail.assessment?.factors?.length" class="factor-list">
              <div v-for="factor in detail.assessment.factors" :key="factor.label" class="factor-row" :class="factor.effect">
                <span>{{ factor.label }}</span>
                <b>{{ typeof factor.value === 'number' && factor.label.includes('потоком') ? `${factor.value}×` : factor.label.includes('документов') ? factor.value : money(factor.value) }}</b>
              </div>
            </div>
            <p class="demo-disclaimer">Расчёт демонстрационный и не заменяет банковский скоринг или решение сотрудника.</p>
          </section>

          <section v-if="detail.events?.length" class="decision-card history-card">
            <h2>История заявки</h2>
            <ol class="event-list">
              <li v-for="event in detail.events" :key="event.id">
                <span></span><div><b>{{ event.note }}</b><small>{{ date(event.createdAt) }}</small></div>
              </li>
            </ol>
          </section>

          <section v-if="canReview" class="decision-card">
            <h2>Решение по заявке</h2>
            <p>Результат увидит клиент в личном кабинете.</p>
            <label for="review-comment">Комментарий клиенту</label>
            <textarea id="review-comment" v-model="comment" rows="4" maxlength="2000" placeholder="Поясните решение или укажите, что нужно дополнить"></textarea>
            <div class="counteroffer-fields">
              <label>Предлагаемая сумма, ₽<input v-model.number="proposedAmount" type="number" min="1" step="1"></label>
              <label>Срок, месяцев<input v-model.number="proposedTermMonths" type="number" min="1" max="120" step="1"></label>
            </div>
            <button class="decision-button approve" type="button" :disabled="saving" @click="decide('approved')">Одобрить заявку</button>
            <button class="decision-button counter" type="button" :disabled="saving" @click="decide('counteroffer')">Предложить другие условия</button>
            <button class="decision-button clarify" type="button" :disabled="saving" @click="decide('needs_info')">Запросить уточнение</button>
            <button class="decision-button reject" type="button" :disabled="saving" @click="decide('rejected')">Отклонить заявку</button>
          </section>
          <section v-else class="decision-card decided-card">
            <h2>{{ statusLabel(detail.status) }}</h2>
            <p>Решение сохранено {{ date(detail.reviewedAt) }}</p>
            <blockquote v-if="detail.reviewComment">{{ detail.reviewComment }}</blockquote>
          </section>
        </aside>
      </div>
    </template>
  </section>
</template>

<style lang="less" scoped src="../staff.less"></style>
<style lang="less" scoped>
@import "@/assets/styles/vars.less";

.review-page { max-width: 1500px; margin: 0 auto; color: #171717; }
.back-link { display: inline-flex; align-items: center; gap: 8px; margin-bottom: 22px; color: #777B82; font-size: 13px; }
.back-link :deep(svg) { width: 12px; height: 12px; transform: rotate(180deg); }
.review-heading { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 22px; }
.review-heading h1 { margin-top: 7px; font-size: 28px; line-height: 36px; }
.review-heading p { margin-top: 5px; color: #777B82; font-size: 14px; }
.review-heading p span { padding: 0 5px; }
.status { flex: 0 0 auto; padding: 7px 12px; border: 1px solid #F6D58A; border-radius: 999px; color: #8A5B00; background: #FFF5D9; font-size: 12px; }
.status.needs_info { border-color: #9ADCF3; color: #17687F; background: #E5F8FE; }
.status.approved { border-color: #A7E6B2; color: #15752A; background: #E9FBEA; }
.status.rejected { border-color: #F0B5B1; color: #A11E16; background: #FFF0EF; }
.client-note { display: flex; flex-direction: column; gap: 5px; margin-bottom: 16px; padding: 14px 16px; border: 1px solid #9ADCF3; border-radius: 12px; color: #17687F; background: #E5F8FE; font-size: 13px; line-height: 19px; }
.review-grid { display: grid; grid-template-columns: minmax(0, 1.65fr) minmax(290px, .85fr); align-items: start; gap: 18px; }
.review-main { display: flex; flex-direction: column; gap: 14px; }
.review-card, .assessment-card, .decision-card { padding: 20px; border: 1px solid #E5E6E8; border-radius: 16px; background: #FFFFFF; }
.section-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 18px; }
.section-heading h2, .decision-card h2 { font-size: 17px; line-height: 22px; }
.section-heading p, .decision-card > p { margin-top: 4px; color: #8B8B8B; font-size: 12px; line-height: 17px; }
.section-icon { display: grid; width: 36px; height: 36px; place-items: center; border-radius: 11px; color: @btnPrimary; background: #FFE2DF; }
.section-icon :deep(svg) { width: 19px; height: 19px; }
.data-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.data-field { display: flex; min-width: 0; flex-direction: column; gap: 5px; padding: 12px; border-radius: 10px; background: #F4F5F6; }
.data-field.full { grid-column: 1 / -1; }
.data-field span, .assessment-number span, .coverage span { color: #858990; font-size: 11px; line-height: 15px; }
.data-field b { overflow-wrap: anywhere; font-size: 13px; line-height: 18px; font-weight: 600; }
.financial-grid .data-field b { font-size: 14px; }
.document-list { display: flex; flex-direction: column; gap: 8px; }
.document-row { display: flex; align-items: center; gap: 11px; padding: 10px; border-radius: 10px; background: #F4F5F6; }
.file-icon { display: grid; width: 36px; height: 36px; flex: 0 0 36px; place-items: center; border: 1px solid #FFB6B0; border-radius: 9px; color: @btnPrimary; background: #FFE2DF; }
.file-icon :deep(svg) { width: 18px; height: 18px; }
.file-info { display: flex; min-width: 0; flex: 1; flex-direction: column; gap: 3px; }
.file-info b { overflow: hidden; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.file-info small { color: #8B8B8B; font-size: 11px; }
.download { flex: 0 0 auto; padding: 7px 10px; border-radius: 8px; color: @btnPrimary; background: #FFF0EF; font-size: 11px; font-weight: 600; }
.documents-empty { padding: 18px; border-radius: 10px; color: #777B82; background: #F4F5F6; font-size: 13px; }
.review-side { position: sticky; top: 100px; display: flex; flex-direction: column; gap: 14px; }
.assessment-card { background: #F2F3F5; }
.assessment-card h2 { margin-top: 7px; font-size: 18px; }
.assessment-note { margin-top: 6px; color: #777B82; font-size: 11px; line-height: 16px; }
.assessment-number { display: flex; justify-content: space-between; gap: 10px; margin-top: 16px; padding-top: 13px; border-top: 1px solid #E0E2E5; }
.assessment-number b { font-size: 13px; text-align: right; }
.coverage { display: flex; align-items: center; justify-content: space-between; margin-top: 16px; padding: 12px; border-radius: 10px; color: #15752A; background: #E9FBEA; }
.coverage b { font-size: 16px; }
.coverage.medium { color: #8A5B00; background: #FFF5D9; }
.coverage.high { color: #A11E16; background: #FFF0EF; }
.factor-list { display: grid; gap: 8px; margin-top: 14px; }
.factor-row { display: flex; justify-content: space-between; gap: 8px; color: #666; font-size: 11px; line-height: 16px; }
.factor-row b { color: #262626; text-align: right; }
.factor-row.warning b { color: #A11E16; }
.factor-row.positive b { color: #15752A; }
.event-list { display: grid; gap: 14px; margin: 16px 0 0; padding: 0; list-style: none; }
.event-list li { display: flex; gap: 10px; }
.event-list li > span { width: 9px; height: 9px; flex: 0 0 9px; margin-top: 4px; border: 2px solid #EF3124; border-radius: 50%; }
.event-list li > div { display: grid; gap: 3px; }
.event-list b { font-size: 12px; line-height: 16px; }
.event-list small { color: #888; font-size: 10px; }
.demo-disclaimer { margin-top: 12px; color: #8B8B8B; font-size: 10px; line-height: 15px; }
.decision-card { box-shadow: 0 8px 24px fade(#000000, 4%); }
.decision-card label { display: block; margin: 17px 0 7px; font-size: 12px; font-weight: 600; }
.decision-card textarea { width: 100%; resize: vertical; padding: 10px 11px; border: 1px solid #D9DADD; border-radius: 10px; outline: none; font-size: 12px; line-height: 18px; }
.decision-card textarea:focus { border-color: #EF3124; box-shadow: 0 0 0 3px fade(#EF3124, 10%); }
.decision-button { width: 100%; margin-top: 9px; padding: 11px; border-radius: 10px; font-size: 13px; font-weight: 600; transition: opacity .18s ease; }
.decision-button:disabled { opacity: .6; cursor: wait; }
.decision-button.approve { color: #FFFFFF; background: #1C9B4B; }
.counteroffer-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; }
.counteroffer-fields label { display: grid; gap: 6px; color: #555; font-size: 11px; font-weight: 600; }
.counteroffer-fields input { min-width: 0; padding: 10px; border: 1px solid #D9DADD; border-radius: 9px; font: inherit; font-size: 12px; }
.decision-button.counter { color: #7A4A00; background: #FFF2CC; }
.decision-button.clarify { color: #6F4D00; background: #FFF2CC; }
.decision-button.reject { color: #A11E16; background: #FFF0EF; }
.decided-card blockquote { margin-top: 14px; padding: 12px; border-left: 3px solid #EF3124; border-radius: 5px; background: #F4F5F6; font-size: 13px; line-height: 19px; }
.feedback { margin-bottom: 14px; padding: 11px 13px; border-radius: 10px; font-size: 13px; }
.feedback.error { color: #A11E16; background: #FFF0EF; }
.review-loading { display: flex; min-height: 260px; align-items: center; justify-content: center; gap: 10px; color: #777B82; font-size: 13px; }
.review-loading span { width: 17px; height: 17px; border: 2px solid #F8D5D2; border-top-color: @btnPrimary; border-radius: 50%; animation: review-spin .7s linear infinite; }
.review-error-page { padding: 40px; border: 1px solid #E5E6E8; border-radius: 16px; background: #FFFFFF; }
.review-error-page h1 { font-size: 20px; }
.review-error-page p { margin-top: 8px; color: #777B82; }
@keyframes review-spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) { .review-grid { grid-template-columns: 1fr; } .review-side { position: static; } }
@media (max-width: 560px) { .review-heading { align-items: flex-start; flex-direction: column; } .review-heading h1 { font-size: 23px; line-height: 30px; } .review-card, .assessment-card, .decision-card { padding: 15px; } .data-grid { gap: 8px; } .data-field { padding: 10px; } }
</style>
