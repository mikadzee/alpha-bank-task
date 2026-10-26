<script setup lang="ts">
import { ref } from "vue";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import { useGlobalStore } from "~/stores";

definePageMeta({ layout: "default" });
const store = useGlobalStore();
const error = ref("");

function newApplication() {
  return navigateTo("/financing?new=1");
}

function openCompany(companyId?: string) {
  if (companyId) store.selectCompany(companyId);
  return navigateTo("/financing?new=1");
}

async function removeCompany(companyId: string, companyName: string) {
  if (!window.confirm(`Удалить сохранённый профиль «${companyName}»? Заявки останутся в истории.`)) return;
  error.value = "";
  try { await store.deleteCompany(companyId); }
  catch { error.value = "Не получилось удалить компанию. Попробуйте ещё раз."; }
}
</script>

<template>
  <section class="company-page">
    <header class="page-heading">
      <div>
        <span class="eyebrow">Профили компаний</span>
        <h1>Мои компании</h1>
        <p>Сохранённые реквизиты можно повторно использовать в новых заявках.</p>
      </div>
      <button type="button" class="primary" @click="newApplication">Новая заявка</button>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="store.companies.length" class="company-list">
      <article v-for="company in store.companies" :key="company.id || company.inn" class="company-card">
        <span class="avatar"><SvgIcon icon="icon-building" /></span>
        <div class="company-info">
          <h2>{{ company.companyName }}</h2>
          <p>ИНН {{ company.inn }}<template v-if="company.ogrn"> · ОГРН {{ company.ogrn }}</template></p>
          <small>{{ company.address || "Адрес не указан" }}</small>
        </div>
        <button class="secondary" type="button" @click="openCompany(company.id)">Использовать в заявке</button>
        <button v-if="company.id" class="delete" type="button" @click="removeCompany(company.id, company.companyName)">Удалить</button>
      </article>
    </div>
    <div v-else class="empty-state">
      <span class="avatar"><SvgIcon icon="icon-building" /></span>
      <h2>Пока нет сохранённых компаний</h2>
      <p>Заполните данные компании при создании первой заявки — профиль появится здесь.</p>
      <button type="button" class="primary" @click="newApplication">Заполнить данные</button>
    </div>
    <p class="notice">Реквизиты в демонстрационном кабинете могут быть синтетическими. Проверяйте их перед отправкой.</p>
  </section>
</template>

<style scoped>
.company-page { display: grid; gap: 22px; }
.page-heading { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.eyebrow { color: #ef3124; font-size: 13px; font-weight: 600; }
h1 { margin: 7px 0; color: #171717; font-size: clamp(25px, 3vw, 34px); }
.page-heading p,.company-info p,.company-info small,.empty-state p { margin: 0; color: #777; }
.primary,.secondary { border: 0; border-radius: 12px; padding: 13px 18px; cursor: pointer; font: inherit; font-weight: 600; }
.primary { color: white; background: #ef3124; }
.secondary { color: #262626; background: #f0f1f3; white-space: nowrap; }
.delete { border: 0; padding: 10px; color: #b42318; background: transparent; font: inherit; cursor: pointer; }
.error { color: #b42318; font-size: 13px; }
.company-list { display: grid; gap: 12px; }
.company-card { display: flex; align-items: center; gap: 16px; padding: 20px; border: 1px solid #e7e7e7; border-radius: 18px; background: white; }
.avatar { display: grid; place-items: center; width: 48px; height: 48px; flex: 0 0 auto; border-radius: 14px; color: #ef3124; background: #fff0ef; }
.avatar :deep(svg) { width: 23px; height: 23px; }
.company-info { flex: 1; min-width: 0; }
.company-info h2 { margin: 0 0 6px; font-size: 18px; }
.company-info small { display: block; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.empty-state { display: grid; justify-items: center; gap: 12px; padding: 54px 24px; border-radius: 20px; background: #f2f3f5; text-align: center; }
.empty-state h2 { margin: 0; font-size: 20px; }
.notice { color: #888; font-size: 13px; }
@media(max-width: 700px) { .page-heading,.company-card { align-items: flex-start; flex-direction: column; } .secondary { width: 100%; } }
</style>
