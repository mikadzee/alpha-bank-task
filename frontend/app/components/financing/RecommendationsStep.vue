<script setup lang="ts">
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import CreditsResult from "~/components/financing/CreditsResult.vue";

type Recommendation = {
  productId: string,
  name: string,
  amount: number,
  termMonths: number,
  annualRate: number,
  monthlyPayment: number,
  totalPayment: number,
  recommended: boolean,
  reasons: {
    title: string,
    description: string
  }[],
  warnings: string[]
};

const props = defineProps<{
  recommendations: Recommendation[],
  submitted: boolean,
  status: string,
  reviewComment?: string | null,
  events?: Array<{ id: string, type: string, note: string, createdAt: string }>,
  offerData?: Record<string, any> | null
}>();

const emit = defineEmits<{
  close: [],
  select: [productId: string],
  offerDecision: [decision: "accept" | "decline"]
}>();
const reviewStates: Record<string, { title: string, description: string, tone: string }> = {
  pending: { title: "Заявка на рассмотрении", description: "Банк проверяет данные и документы. Статус появится здесь после решения.", tone: "pending" },
  approved: { title: "Заявка одобрена", description: "Банк подтвердил финансирование. Дальнейшие шаги согласуются с менеджером банка.", tone: "approved" },
  rejected: { title: "Банк не одобрил заявку", description: "Решение относится к этой заявке. Вы можете изменить параметры и отправить новую.", tone: "rejected" },
  needs_info: { title: "Нужно дополнить заявку", description: "Банк запросил уточнения. Вернитесь к данным заявки, внесите изменения и отправьте её повторно.", tone: "needs-info" },
  offer_made: { title: "Банк предлагает другие условия", description: "Проверьте сумму, срок и примерный платёж. Условия станут согласованными только после вашего ответа.", tone: "pending" },
  offer_accepted: { title: "Условия приняты", description: "Вы согласились с предложенными параметрами. Сотрудник банка свяжется с вами для следующих шагов.", tone: "approved" },
  offer_declined: { title: "Предложение отклонено", description: "Предложение банка закрыто. Вы можете начать новую заявку с другими параметрами.", tone: "needs-info" }
};
const eventLabels: Record<string, string> = {
  draft_created: "Создан черновик",
  submitted: "Заявка отправлена в банк",
  client_updated: "Вы внесли изменения",
  resubmitted: "Исправленная заявка отправлена повторно",
  decision: "Банк зафиксировал решение",
  accept: "Вы приняли условия банка",
  decline: "Вы отклонили условия банка"
};
const eventDate = (value: string) => new Intl.DateTimeFormat("ru-RU", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
const money = (value?: number) => value == null ? "—" : `${new Intl.NumberFormat("ru-RU").format(value)} ₽`;
</script>

<template>
  <section class="card recommendations">
    <button class="close" type="button" @click="emit('close')">×</button>

    <div class="heading">
      <h1>{{ props.submitted ? "Результат по заявке" : "Подходящие предложения" }}</h1>
      <p>{{ props.submitted ? "Текущий статус и дальнейшие действия" : "Предложения рассчитаны по данным вашей компании и условиям кредитных продуктов" }}</p>
    </div>

    <div v-if="props.submitted" class="submitted">
      <span class="success" :class="reviewStates[props.status]?.tone"><b v-if="props.status === 'rejected'">×</b><SvgIcon v-else icon="icon-upload-success" /></span>
      <h2>{{ reviewStates[props.status]?.title || "Заявка отправлена" }}</h2>
      <p>{{ reviewStates[props.status]?.description || "Заявка передана в банк." }}</p>
      <p v-if="props.reviewComment" class="review-comment">Комментарий банка: {{ props.reviewComment }}</p>
      <section v-if="props.offerData" class="counteroffer">
        <h3>{{ props.offerData.productName || "Предложенные условия" }}</h3>
        <div><span>Сумма</span><b>{{ money(props.offerData.amount) }}</b></div>
        <div><span>Срок</span><b>{{ props.offerData.termMonths }} месяцев</b></div>
        <div><span>Ставка</span><b>{{ props.offerData.annualRate }}% годовых</b></div>
        <div><span>Платёж в месяц</span><b>≈ {{ money(props.offerData.monthlyPayment) }}</b></div>
        <div class="total"><span>Общая сумма выплат</span><b>≈ {{ money(props.offerData.totalPayment) }}</b></div>
      </section>
      <div v-if="props.status === 'offer_made'" class="offer-actions">
        <button class="accept-offer" type="button" @click="emit('offerDecision', 'accept')">Принять условия</button>
        <button class="decline-offer" type="button" @click="emit('offerDecision', 'decline')">Отклонить предложение</button>
      </div>
      <NuxtLink v-if="props.status === 'offer_declined'" class="new-request" to="/financing?new=1">Подать новую заявку</NuxtLink>
      <ol v-if="props.events?.length" class="timeline">
        <li v-for="event in props.events" :key="event.id">
          <span class="timeline-dot"></span>
          <div><b>{{ eventLabels[event.type] || event.note }}</b><small>{{ eventDate(event.createdAt) }}</small><p v-if="event.type === 'decision' && event.note !== 'Решение банка зафиксировано'">{{ event.note }}</p></div>
        </li>
      </ol>
      <NuxtLink v-if="props.status === 'rejected'" class="new-request" to="/financing?new=1">Подать новую заявку</NuxtLink>
    </div>

    <div v-else-if="!props.recommendations.length" class="empty">
      Подходящих предложений пока нет. Проверьте сумму, срок и данные о компании.
    </div>

    <div v-else class="list">
      <CreditsResult
        v-for="offer in props.recommendations"
        :key="offer.productId"
        :offer="offer"
        @select="emit('select', $event)"
      />
    </div>
  </section>
</template>

<style lang="less" scoped src="./recommendations-step.less"></style>
