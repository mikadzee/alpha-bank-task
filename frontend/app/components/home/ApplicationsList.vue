<script setup lang="ts">
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";

type Application = {
  id: string,
  status?: string,
  companyData?: {
    companyName?: string,
    inn?: string
  },
  financialData?: {
    requestedAmount?: number,
    purpose?: string
  },
  reviewComment?: string | null,
  submittedAt?: string | null,
  createdAt?: string,
  updatedAt?: string
};

const props = defineProps<{
  applications: Application[]
}>();

const emit = defineEmits<{
  create: [],
  open: [id: string]
}>();

const formatMoney = (value?: number) => value ? `${new Intl.NumberFormat("ru-RU").format(value)} ₽` : "Сумма не указана";
const statusLabels: Record<string, string> = {
  pending: "Ожидает решения",
  needs_info: "Нужно уточнение",
  approved: "Одобрено",
  rejected: "Отказано",
  offer_made: "Ждёт вашего ответа",
  offer_accepted: "Условия приняты",
  offer_declined: "Предложение отклонено",
  draft: "Черновик"
};
const getStatus = (status?: string) => statusLabels[status || ""] || "Черновик";
const purposeLabels: Record<string, string> = {
  working_capital: "Оборотный кредит",
  equipment: "Кредит на оборудование",
  business_expansion: "Кредит на развитие бизнеса",
  other: "Кредит на любые бизнес-цели"
};
const getProductName = (application: Application) => purposeLabels[application.financialData?.purpose || ""] || "Заявка на финансирование";
const getReference = (id: string) => `Заявка № ${id.slice(0, 8).toUpperCase()}`;
const getDate = (value?: string | null) => value ? new Date(value).toLocaleDateString("ru-RU", { day: "numeric", month: "short", year: "numeric" }) : "Дата не указана";
</script>

<template>
  <section class="applications">
    <div class="heading">
      <h2>Мои заявки</h2>
      <button v-if="props.applications.length" type="button" @click="emit('create')">Новая заявка</button>
    </div>

    <div v-if="!props.applications.length" class="empty">
      <SvgIcon icon="icon-clipboard" />
      <h3>Здесь появятся ваши заявки</h3>
      <p>Когда вы подберёте финансирование и отправите заявку, здесь можно будет следить за её статусом и следующими шагами.</p>
      <button type="button" @click="emit('create')">
        Подобрать финансирование
        <SvgIcon icon="icon-arrow-right" />
      </button>
    </div>

    <div v-else class="list">
      <div
        v-for="application in props.applications"
        :key="application.id"
        class="application-entry"
      >
        <button
          class="application-row"
          type="button"
          @click="emit('open', application.id)"
        >
          <span class="application-title">
            <b>{{ getProductName(application) }}</b>
            <small>{{ application.companyData?.companyName || "Новая компания" }}<template v-if="application.companyData?.inn"> · ИНН {{ application.companyData.inn }}</template> · {{ getReference(application.id) }}</small>
          </span>
          <span class="application-amount-date">
            <b>{{ formatMoney(application.financialData?.requestedAmount) }}</b>
            <small>{{ getDate(application.submittedAt || application.createdAt) }}</small>
          </span>
          <span class="application-status" :class="application.status">
            {{ getStatus(application.status) }}
          </span>
        </button>
        <p v-if="application.reviewComment && application.status === 'needs_info'" class="application-review-note">
          Комментарий банка: {{ application.reviewComment }}
        </p>
      </div>
    </div>
  </section>
</template>

<style lang="less" scoped src="./applications-list.less"></style>
