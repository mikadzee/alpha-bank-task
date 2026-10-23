<script setup lang="ts">
import AppInput from "~/components/shared/input/AppInput.vue";

type FinanceData = {
  revenue: string,
  term: string,
  expenses: string,
  amount: string,
  purpose: string,
  details: string,
  otherPurpose: string
};

defineProps<{
  finance: FinanceData
}>();

const emit = defineEmits<{
  close: [],
  apply: []
}>();

const purposes = [
  { value: "equipment", label: "Покупка оборудования" },
  { value: "working-capital", label: "Пополнение оборотных средств" },
  { value: "expansion", label: "Развитие и расширение бизнеса" },
  { value: "refinancing", label: "Рефинансирование" },
  { value: "other", label: "Другая цель" }
];

const purposeLabel = (value: string) => purposes.find((item) => item.value === value)?.label || "";
</script>

<template>
  <form class="card finance" @submit.prevent="emit('apply')">
    <button class="close" type="button" @click="emit('close')">×</button>

    <div class="heading">
      <h1>Финансовые показатели</h1>
      <p>Укажите основные финансовые данные о бизнесе</p>
    </div>

    <div class="fields">
      <div class="row">
        <AppInput
          v-model="finance.revenue"
          name="revenue"
          label="Выручка за последний год"
          inputmode="numeric"
          format="amount"
          suffix="₽"
          required
        />
        <label class="select">
          <span>Срок кредита</span>
          <select v-model="finance.term" required>
            <option value="12 месяцев">12 месяцев</option>
            <option value="24 месяца">24 месяца</option>
            <option value="36 месяцев">36 месяцев</option>
            <option value="60 месяцев">60 месяцев</option>
          </select>
          <i></i>
        </label>
      </div>

      <div class="row">
        <AppInput
          v-model="finance.expenses"
          name="expenses"
          label="Ежемесячные расходы"
          inputmode="numeric"
          format="amount"
          suffix="₽"
          required
        />
        <AppInput
          v-model="finance.amount"
          name="amount"
          label="Желаемая сумма кредита"
          inputmode="numeric"
          format="amount"
          suffix="₽"
          required
        />
      </div>

      <label class="select wide purpose" :class="{ 'has-purpose': finance.purpose }">
        <span v-if="finance.purpose" class="label">Цель финансирования</span>
        <span class="value">{{ purposeLabel(finance.purpose) || "Цель финансирования" }}</span>
        <select v-model="finance.purpose" required>
          <option value="" disabled>Цель финансирования</option>
          <option v-for="purpose in purposes" :key="purpose.value" :value="purpose.value">{{ purpose.label }}</option>
        </select>
        <i></i>
      </label>

      <AppInput
        v-if="finance.purpose === 'other'"
        v-model="finance.otherPurpose"
        name="other-purpose"
        label="Укажите цель финансирования"
        required
      />

      <textarea
        v-model="finance.details"
        class="details"
        placeholder="Подробности (необязательно)"
        rows="2"
      ></textarea>
    </div>

    <button class="apply" type="submit">Применить</button>
  </form>
</template>

<style lang="less" scoped src="./finance-step.less"></style>
