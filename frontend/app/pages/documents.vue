<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useGlobalStore } from "~/stores";

definePageMeta({ layout: "default" });
const store = useGlobalStore();
const error = ref("");
const downloading = ref("");
const documents = computed(() => store.applications.flatMap((application: any) =>
  (application.documents || []).map((document: any) => ({ ...document, application }))
));
const labels: Record<string, string> = {
  egrul_extract: "Выписка из ЕГРЮЛ/ЕГРИП",
  accounting_report: "Бухгалтерская отчётность",
  tax_certificate: "Справка о налоговой задолженности",
  bank_statement: "Выписка по расчётному счёту",
  other: "Дополнительный документ"
};

onMounted(async () => {
  if (!store.applications.length) {
    try { await store.loadApplications(); } catch { error.value = "Не удалось загрузить список документов."; }
  }
});

async function download(item: any) {
  downloading.value = item.documentId || item.id;
  error.value = "";
  try {
    await store.downloadDocument(item.application.id, item.documentId || item.id, item.originalName || "document");
  } catch {
    error.value = "Не удалось скачать файл. Возможно, документ уже удалён.";
  } finally {
    downloading.value = "";
  }
}
</script>

<template>
  <section class="documents-page">
    <header class="page-heading">
      <span class="eyebrow">Файлы заявок</span>
      <h1>Документы</h1>
      <p>Загруженные файлы сгруппированы по компаниям и заявкам.</p>
    </header>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="documents.length" class="document-list">
      <article v-for="item in documents" :key="item.documentId || item.id" class="document-row">
        <span class="file-mark">PDF</span>
        <div class="document-info">
          <b>{{ labels[item.type] || item.type }}</b>
          <span>{{ item.application.companyData?.companyName || "Компания не указана" }} · Заявка № {{ item.application.id.slice(0, 8).toUpperCase() }}</span>
          <small>{{ item.originalName }} · {{ item.sizeBytes ? `${(item.sizeBytes / 1024 / 1024).toFixed(1)} МБ` : "файл" }}</small>
        </div>
        <button type="button" :disabled="downloading === (item.documentId || item.id)" @click="download(item)">
          {{ downloading === (item.documentId || item.id) ? "Открываем…" : "Скачать" }}
        </button>
      </article>
    </div>
    <div v-else-if="!error" class="empty">
      <h2>Документов пока нет</h2>
      <p>После загрузки они появятся здесь вместе с соответствующей заявкой.</p>
      <NuxtLink to="/financing?new=1">Начать заявку</NuxtLink>
    </div>
    <p class="disclaimer">Файлы доступны только владельцу заявки и проверяющему сотруднику банка.</p>
  </section>
</template>

<style scoped>
.documents-page { display: grid; gap: 20px; }
.page-heading { padding-top: 8px; }
.eyebrow { color: #ef3124; font-size: 13px; font-weight: 600; }
h1 { margin: 7px 0; color: #171717; font-size: clamp(25px, 3vw, 34px); }
.page-heading p,.document-info span,.document-info small,.disclaimer { color: #777; }
.document-list { display: grid; gap: 10px; }
.document-row { display: flex; align-items: center; gap: 14px; padding: 16px; border: 1px solid #e8e8e8; border-radius: 16px; background: white; }
.file-mark { display: grid; place-items: center; width: 44px; height: 48px; border-radius: 12px; color: #ef3124; background: #fff0ef; font-size: 11px; font-weight: 700; }
.document-info { display: grid; gap: 4px; flex: 1; min-width: 0; }
.document-info span,.document-info small { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
button,.empty a { border: 0; border-radius: 10px; padding: 11px 15px; color: #fff; background: #ef3124; font: inherit; font-weight: 600; text-decoration: none; cursor: pointer; }
button:disabled { opacity: .65; cursor: wait; }
.empty { display: grid; justify-items: center; gap: 10px; padding: 48px; border-radius: 18px; background: #f2f3f5; text-align: center; }
.empty h2,.empty p { margin: 0; }
.disclaimer,.error { font-size: 13px; }
.error { color: #bd271e; }
@media(max-width:620px) { .document-row { align-items: flex-start; flex-wrap: wrap; } .document-info { flex-basis: calc(100% - 60px); } button { margin-left: 58px; } }
</style>
