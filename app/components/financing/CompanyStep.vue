<script setup lang="ts">
import AppInput from "~/components/shared/input/AppInput.vue";
import CheckerHelper from "~/components/shared/status/CheckerHelper.vue";

type CompanyData = {
  inn: string,
  ogrn: string,
  name: string,
  address: string,
  activity: string,
  otherActivity: string
};

defineProps<{
  company: CompanyData,
  companyFound: boolean | null
}>();

const emit = defineEmits<{
  close: [],
  apply: [],
  lookup: [inn: string]
}>();

const activities = [
  { value: "28.99", label: "Производственное оборудование (ОКВЭД 28.99)" },
  { value: "46.90", label: "Оптовая торговля (ОКВЭД 46.90)" },
  { value: "82.99", label: "Услуги для бизнеса (ОКВЭД 82.99)" },
  { value: "other", label: "Другое" }
];

const activityLabel = (value: string) => activities.find((item) => item.value === value)?.label || "";
</script>

<template>
  <form class="card company" @submit.prevent="emit('apply')">
    <button class="close" type="button" @click="emit('close')">×</button>

    <div class="heading">
      <h1>Проверить данные компании</h1>
      <p>Мы автоматически заполняем часть данных по ИНН. Проверьте и при необходимости отредактируйте</p>
    </div>

    <div class="fields">
      <div class="inn">
        <AppInput
          v-model="company.inn"
          name="inn"
          label="ИНН"
          inputmode="numeric"
          format="digits"
          :max-length="12"
          autocomplete="off"
          @blur="emit('lookup', company.inn)"
          required
        />
        <CheckerHelper
          v-if="companyFound !== null"
          :type="companyFound ? 'success' : 'error'"
          :text="companyFound ? 'Найден' : 'Не найден'"
        />
      </div>

      <AppInput
        v-model="company.ogrn"
        name="ogrn"
        label="ОГРН"
        inputmode="numeric"
        format="digits"
        :max-length="13"
        autocomplete="off"
      />

      <div class="row">
        <AppInput
          v-model="company.name"
          name="company-name"
          label="Название компании"
          autocomplete="organization"
          required
        />
        <AppInput
          v-model="company.address"
          name="company-address"
          label="Адрес"
          autocomplete="street-address"
        />
      </div>

      <label class="select activity-select" :class="{ 'has-activity': company.activity }">
        <span class="label">Вид деятельности</span>
        <span class="value">{{ activityLabel(company.activity) || "Выберите вид деятельности" }}</span>
        <select v-model="company.activity" required>
          <option value="" disabled>Выберите вид деятельности</option>
          <option v-for="activity in activities" :key="activity.value" :value="activity.value">{{ activity.label }}</option>
        </select>
        <i></i>
      </label>

      <AppInput
        v-if="company.activity === 'other'"
        v-model="company.otherActivity"
        name="other-activity"
        label="Укажите вид деятельности"
        required
      />
    </div>

    <button class="apply" type="submit">Применить</button>
  </form>
</template>

<style lang="less" scoped src="./company-step.less"></style>
