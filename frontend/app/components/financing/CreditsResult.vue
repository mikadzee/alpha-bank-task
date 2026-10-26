<script setup lang="ts">
import { ref } from "vue";
import CheckerHelper from "~/components/shared/status/CheckerHelper.vue";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";

type RecommendationReason = {
  title: string,
  description: string
};

type Recommendation = {
  productId: string,
  name: string,
  amount: number,
  termMonths: number,
  annualRate: number,
  monthlyPayment: number,
  totalPayment: number,
  recommended: boolean,
  reasons: RecommendationReason[],
  warnings: string[]
};

const props = defineProps<{
  offer: Recommendation
}>();

const emit = defineEmits<{
  select: [productId: string]
}>();

const expanded = ref(false);
const formatMoney = (value: number) => new Intl.NumberFormat("ru-RU").format(value);

function getTerm(months: number) {
  const lastDigit = months % 10;
  const lastTwoDigits = months % 100;

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return `${months} месяцев`;
  }

  if (lastDigit === 1) {
    return `${months} месяц`;
  }

  if (lastDigit >= 2 && lastDigit <= 4) {
    return `${months} месяца`;
  }

  return `${months} месяцев`;
}
</script>

<template>
  <article class="offer">
    <CheckerHelper v-if="props.offer.recommended" text="Рекомендуем" type="success" />
    <h2 class="title">{{ props.offer.name }}</h2>

    <div class="fields">
      <div class="field">
        <div class="content">
          <p class="hint">Рекомендуемая сумма</p>
          <p class="value">{{ formatMoney(props.offer.amount) }} ₽</p>
        </div>
        <div class="content">
          <p class="hint">Срок</p>
          <p class="value">{{ getTerm(props.offer.termMonths) }}</p>
        </div>
      </div>

      <div class="field">
        <div class="content">
          <p class="hint">Ставка</p>
          <p class="value">от {{ props.offer.annualRate }}% годовых</p>
        </div>
        <div class="content">
          <p class="hint">Платёж в месяц</p>
          <p class="value">≈ {{ formatMoney(props.offer.monthlyPayment) }} ₽</p>
        </div>
      </div>
    </div>

    <button class="explain" type="button" @click="expanded = !expanded">
      <span>Как рассчитано предложение</span>
      <SvgIcon icon="icon-arrow-bottom" :class="{ opened: expanded }" />
    </button>

    <div v-if="expanded" class="details">
      <div v-for="reason in props.offer.reasons" :key="reason.title" class="reason">
        <b>{{ reason.title }}</b>
        <p>{{ reason.description }}</p>
      </div>

      <div class="total">
        <p>Общая сумма выплат</p>
        <b>≈ {{ formatMoney(props.offer.totalPayment) }} ₽</b>
      </div>

      <div v-if="props.offer.warnings.length" class="warning">
        <span class="warning-icon">!</span>
        <p>
          <b>Что важно учесть</b>
          {{ props.offer.warnings.join(" ") }}
        </p>
      </div>
    </div>

    <button class="choose" type="button" @click="emit('select', props.offer.productId)">
      Подать заявку
    </button>
  </article>
</template>

<style lang="less" scoped src="./credits-result.less"></style>
