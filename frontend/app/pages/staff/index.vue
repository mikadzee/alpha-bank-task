<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import { useGlobalStore } from "~/stores";

definePageMeta({ layout: "default" });

const store = useGlobalStore();
const filter = ref("pending");
const search = ref("");
const loading = ref(false);
const error = ref("");
const filterOptions = [
  { value: "pending", label: "На рассмотрении" },
  { value: "needs_info", label: "Нужно уточнение" },
  { value: "approved", label: "Одобрены" },
  { value: "offer_made", label: "Ждут ответа клиента" },
  { value: "rejected", label: "Отклонены" },
  { value: "all", label: "Все заявки" }
];
const statusLabels: Record<string, string> = {
  pending: "На рассмотрении",
  needs_info: "Нужно уточнение",
  approved: "Одобрена",
  rejected: "Отклонена",
  offer_made: "Предложены другие условия",
  offer_accepted: "Условия приняты",
  offer_declined: "Предложение отклонено"
};

async function load() {
  loading.value = true;
  error.value = "";
  try {
    await store.loadStaffApplications(filter.value, search.value);
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : "Не удалось загрузить очередь заявок";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(filter, load);

const date = (value?: string) => value
  ? new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value))
  : "Дата не указана";
const money = (value?: number) => value
  ? `${new Intl.NumberFormat("ru-RU").format(value)} ₽`
  : "Не указана";
const statusLabel = (value: string) => statusLabels[value] || value;
</script>

<template>
  <section class="staff-page">
    <header class="staff-heading">
      <div>
        <span class="eyebrow">Рабочее место банка</span>
        <h1>Заявки на рассмотрении</h1>
        <p>Проверьте данные и документы, затем зафиксируйте результат рассмотрения.</p>
      </div>
      <div class="queue-total">
        <b>{{ store.staffApplications.length }}</b>
        <span>{{ filter === "pending" ? "в очереди" : "в списке" }}</span>
      </div>
    </header>

    <section class="queue-card">
      <div class="queue-toolbar">
        <div class="filter-tabs" role="tablist" aria-label="Фильтр заявок">
          <button
            v-for="option in filterOptions"
            :key="option.value"
            type="button"
            :class="{ active: filter === option.value }"
            @click="filter = option.value"
          >{{ option.label }}</button>
        </div>
        <form class="search" @submit.prevent="load">
          <SvgIcon icon="icon-search" />
          <input v-model="search" aria-label="Поиск заявок" placeholder="Компания, ИНН или email">
          <button type="submit">Найти</button>
        </form>
      </div>

      <p v-if="error" class="feedback error">{{ error }}</p>
      <div v-if="loading" class="queue-loading"><span></span>Обновляем список</div>
      <div v-else-if="!store.staffApplications.length" class="queue-empty">
        <span class="empty-icon"><SvgIcon icon="icon-clipboard" /></span>
        <h2>Заявок пока нет</h2>
        <p>Отправленные клиентами заявки появятся здесь. Новые заявки автоматически попадут в очередь на рассмотрение.</p>
      </div>
      <div v-else class="application-list">
        <NuxtLink
          v-for="application in store.staffApplications"
          :key="application.id"
          :to="`/staff/applications/${application.id}`"
          class="application-row"
        >
          <span class="company-avatar"><SvgIcon icon="icon-building" /></span>
          <span class="company-main">
            <b>{{ application.companyData?.companyName || "Компания не указана" }}</b>
            <small>ИНН {{ application.companyData?.inn || "—" }} · {{ application.clientEmail }}</small>
          </span>
          <span class="request-main">
            <b>{{ money(application.financialData?.requestedAmount) }}</b>
            <small>{{ application.productName || "Кредитное предложение" }}</small>
          </span>
          <span class="row-meta">
            <span class="status" :class="application.status">{{ statusLabel(application.status) }}</span>
            <small>{{ date(application.submittedAt) }}</small>
          </span>
          <SvgIcon class="row-arrow" icon="icon-arrow-right" />
        </NuxtLink>
      </div>
    </section>
  </section>
</template>

<style lang="less" scoped src="./staff.less"></style>
