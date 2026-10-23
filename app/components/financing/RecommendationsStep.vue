<script setup lang="ts">
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";

type Recommendation = {
  productId: string,
  name: string,
  amount: number,
  termMonths: number,
  annualRate: number,
  monthlyPayment: number,
  totalPayment: number,
  recommended: boolean,
  reasons: string[],
  warnings: string[]
};

const props = defineProps<{
  recommendations: Recommendation[],
  submitted: boolean,
  status: string
}>();

const emit = defineEmits<{
  close: [],
  select: [productId: string]
}>();

const formatMoney = (value: number) => new Intl.NumberFormat("ru-RU").format(value);
</script>

<template>
  <section class="card recommendations">
    <button class="close" type="button" @click="emit('close')">×</button>

    <div class="heading">
      <h1>{{ props.submitted ? "Заявка отправлена" : "Подходящие предложения" }}</h1>
      <p>{{ props.submitted ? "Заявка передана на рассмотрение" : "Выберите вариант финансирования для вашей компании" }}</p>
    </div>

    <div v-if="props.submitted" class="submitted">
      <span class="success"><SvgIcon icon="icon-upload-success" /></span>
      <h2>Заявка на рассмотрении</h2>
      <p>Текущий статус: {{ props.status || "pending" }}</p>
    </div>

    <div v-else-if="!props.recommendations.length" class="empty">
      Подходящих предложений пока нет. Проверьте сумму, срок и данные о компании.
    </div>

    <div v-else class="list">
      <article v-for="offer in props.recommendations" :key="offer.productId" class="offer">
        <div class="offer-heading">
          <h2>{{ offer.name }}</h2>
          <span v-if="offer.recommended" class="badge">Рекомендуем</span>
        </div>

        <div class="numbers">
          <p><span>Сумма</span><b>{{ formatMoney(offer.amount) }} ₽</b></p>
          <p><span>Срок</span><b>{{ offer.termMonths }} месяцев</b></p>
          <p><span>Ставка</span><b>{{ offer.annualRate }}% годовых</b></p>
          <p><span>Платёж в месяц</span><b>{{ formatMoney(offer.monthlyPayment) }} ₽</b></p>
        </div>

        <ul v-if="offer.reasons.length" class="reasons">
          <li v-for="reason in offer.reasons" :key="reason">{{ reason }}</li>
        </ul>
        <p v-if="offer.warnings.length" class="warning">{{ offer.warnings.join(" · ") }}</p>

        <button class="choose" type="button" @click="emit('select', offer.productId)">Подать заявку</button>
      </article>
    </div>
  </section>
</template>

<style lang="less" scoped src="./recommendations-step.less"></style>
