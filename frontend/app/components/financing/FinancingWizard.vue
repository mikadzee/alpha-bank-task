<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { onBeforeRouteLeave } from "vue-router";
import FinancingProgress from "~/components/financing/Progress.vue";
import CompanyStep from "~/components/financing/CompanyStep.vue";
import FinanceStep from "~/components/financing/FinanceStep.vue";
import DocumentsStep from "~/components/financing/DocumentsStep.vue";
import RecommendationsStep from "~/components/financing/RecommendationsStep.vue";
import { useFinancingStore } from "~/stores/financing";
import { useGlobalStore } from "~/stores";

const financing = useFinancingStore();
const global = useGlobalStore();
const route = useRoute();
const router = useRouter();
const isReady = ref(false);
const isHydrating = ref(false);
let companySaveTimer: ReturnType<typeof setTimeout> | null = null;
let financeSaveTimer: ReturnType<typeof setTimeout> | null = null;

const formatMoney = (value?: number | string) => value ? new Intl.NumberFormat("ru-RU").format(Number(value)) : "";

function restoreApplication() {
  const application = global.application;

  if (!application) {
    return;
  }

  const company = application.companyData || {};
  const finance = application.financialData || {};

  Object.assign(financing.company, {
    inn: String(company.inn || ""),
    ogrn: String(company.ogrn || ""),
    name: company.companyName || "",
    address: company.address || "",
    activity: ["28.99", "46.90", "82.99"].includes(company.okved || "") ? company.okved : company.okved ? "other" : "",
    otherActivity: ["28.99", "46.90", "82.99"].includes(company.okved || "") ? "" : company.okved || ""
  });

  const purposeMap: Record<string, string> = {
    working_capital: "working-capital",
    business_expansion: "expansion"
  };

  Object.assign(financing.finance, {
    revenue: formatMoney(finance.annualRevenue),
    term: finance.requestedTermMonths ? `${finance.requestedTermMonths} месяцев` : financing.finance.term,
    expenses: formatMoney(finance.monthlyExpenses),
    amount: formatMoney(finance.requestedAmount),
    purpose: purposeMap[finance.purpose] || finance.purpose || "",
    details: finance.purpose === "other" ? "" : finance.purposeDetails || "",
    otherPurpose: finance.purpose === "other" ? finance.purposeDetails || "" : ""
  });

  const documents = application.documents || application.uploadedDocuments || [];

  documents.forEach((item: Record<string, any>) => {
    let document = financing.documents.find((current) => current.type === item.type && current.status !== "success");

    if (!document && item.type === "other") {
      financing.addDocument();
      document = financing.documents[financing.documents.length - 1];
    }

    if (document) {
      document.documentId = item.documentId || item.id || "";
      document.fileName = item.originalName || item.fileName || "";
      document.status = "success";
    }
  });

  if (["pending", "approved", "rejected", "offer_made", "offer_accepted", "offer_declined"].includes(application.status || "")) {
    financing.submitted = true;
    financing.step = 3;
  } else if (application.status === "needs_info") {
    financing.submitted = false;
    financing.step = 0;
  } else if (documents.length) {
    financing.step = 2;
  } else if (finance.annualRevenue) {
    financing.step = 1;
  }
}

function clearSaveTimers() {
  if (companySaveTimer) {
    clearTimeout(companySaveTimer);
    companySaveTimer = null;
  }

  if (financeSaveTimer) {
    clearTimeout(financeSaveTimer);
    financeSaveTimer = null;
  }
}

async function flushAutosaves() {
  if (companySaveTimer) {
    clearTimeout(companySaveTimer);
    companySaveTimer = null;
    await global.autosaveCompanyDraft({ ...financing.company });
  }

  if (financeSaveTimer) {
    clearTimeout(financeSaveTimer);
    financeSaveTimer = null;
    await global.autosaveFinanceDraft({ ...financing.finance });
  }
}

watch(() => financing.company, () => {
  if (!isReady.value || isHydrating.value || financing.step !== 0) {
    return;
  }

  if (companySaveTimer) clearTimeout(companySaveTimer);
  companySaveTimer = setTimeout(() => {
    companySaveTimer = null;
    void global.autosaveCompanyDraft({ ...financing.company });
  }, 700);
}, { deep: true, flush: "sync" });

watch(() => financing.finance, () => {
  if (!isReady.value || isHydrating.value || financing.step !== 1) {
    return;
  }

  if (financeSaveTimer) clearTimeout(financeSaveTimer);
  financeSaveTimer = setTimeout(() => {
    financeSaveTimer = null;
    void global.autosaveFinanceDraft({ ...financing.finance });
  }, 700);
}, { deep: true, flush: "sync" });

function fillSelectedCompany() {
  if (!global.company) {
    return;
  }

  const okved = global.company.okved;
  const knownActivity = ["28.99", "46.90", "82.99"].includes(okved);

  Object.assign(financing.company, {
    inn: global.company.inn,
    ogrn: global.company.ogrn,
    name: global.company.companyName,
    address: global.company.address,
    activity: knownActivity ? okved : okved ? "other" : "",
    otherActivity: knownActivity ? "" : okved
  });
}

onMounted(async () => {
  const isNew = route.query.new === "1";
  const routeApplicationId = String(route.query.applicationId || "");

  try {
    isHydrating.value = true;

    if (isNew || (!routeApplicationId && !["draft", "needs_info"].includes(global.application?.status || ""))) {
      financing.reset();
      const application = await global.createApplication();
      fillSelectedCompany();
      await router.replace({ path: route.path, query: { applicationId: application.id } });
      return;
    }

    const applicationId = routeApplicationId || global.applicationId;

    if (applicationId) {
      financing.reset();
      await global.loadApplication(applicationId);
    }

    restoreApplication();
  } catch {
    global.error ||= "Не удалось открыть заявку. Попробуйте ещё раз.";
  } finally {
    isHydrating.value = false;
    isReady.value = true;
  }
});

onBeforeUnmount(clearSaveTimers);
onBeforeRouteLeave(flushAutosaves);

async function closeForm() {
  await flushAutosaves();
  await navigateTo("/");
}

async function lookupCompany(inn: string) {
  try {
    const found = await global.lookupCompany(inn);

    if (found && global.company) {
      const okved = global.company.okved;
      const knownActivity = ["28.99", "46.90", "82.99"].includes(okved);

      Object.assign(financing.company, {
        inn: global.company.inn,
        ogrn: global.company.ogrn,
        name: global.company.companyName,
        address: global.company.address,
        activity: knownActivity ? okved : okved ? "other" : "",
        otherActivity: knownActivity ? "" : okved
      });
    }
  } catch {
    return;
  }
}

async function saveCompany() {
  if (companySaveTimer) clearTimeout(companySaveTimer);
  companySaveTimer = null;

  if (!/^(\d{10}|\d{12})$/.test(financing.company.inn)) {
    global.error = "ИНН должен содержать 10 или 12 цифр";
    return;
  }

  if (financing.company.ogrn && !/^(\d{13}|\d{15})$/.test(financing.company.ogrn)) {
    global.error = "ОГРН/ОГРНИП должен содержать 13 или 15 цифр";
    return;
  }

  try {
    await global.saveCompany(financing.company);
    financing.nextStep();
  } catch {
    return;
  }
}

async function saveFinance() {
  if (financeSaveTimer) clearTimeout(financeSaveTimer);
  financeSaveTimer = null;

  try {
    await global.saveFinance(financing.finance);
    financing.nextStep();
  } catch {
    return;
  }
}

async function uploadDocument(id: string, file: File) {
  const document = financing.documents.find((item) => item.id === id);

  if (!document) {
    return;
  }

  try {
    const result = await global.uploadDocument(document.type, file) as { documentId?: string, id?: string };
    financing.setDocumentUploaded(id, file, result.documentId || result.id || "");
  } catch {
    financing.setDocumentError(id);
  }
}

async function loadRecommendations() {
  const requiredDocumentMissing = financing.documents.some((document) => document.required && document.status !== "success");

  if (requiredDocumentMissing) {
    global.error = "Загрузите все обязательные документы";
    return;
  }

  try {
    await global.saveFinance(financing.finance);
    await global.loadRecommendations();
    financing.nextStep();
  } catch {
    return;
  }
}

async function submitApplication(productId: string) {
  try {
    await global.submitApplication(productId);
    financing.setSubmitted();
  } catch {
    return;
  }
}

async function decideOffer(decision: "accept" | "decline") {
  try {
    await global.decideOffer(decision);
  } catch {
    return;
  }
}
</script>

<template>
  <section class="financing">
    <div v-if="!isReady" class="form-loading">
      <span class="form-loading__spinner"></span>
      <p>Открываем заявку</p>
    </div>
    <template v-else>
      <FinancingProgress :step="financing.step" />
      <p v-if="global.application?.status === 'needs_info' && global.application?.reviewComment" class="review-request">
        <b>Банк запросил уточнение</b>{{ global.application.reviewComment }}
      </p>
      <p v-if="global.error" class="request-error">{{ global.error }}</p>

      <CompanyStep
        v-if="financing.step === 0"
        :company="financing.company"
        :company-found="global.companyLookupFound"
        @close="closeForm"
        @lookup="lookupCompany"
        @apply="saveCompany"
      />

      <FinanceStep
        v-else-if="financing.step === 1"
        :finance="financing.finance"
        @close="closeForm"
        @apply="saveFinance"
      />

      <DocumentsStep
        v-else-if="financing.step === 2"
        :documents="financing.documents"
        @close="closeForm"
        @apply="loadRecommendations"
        @add="financing.addDocument"
        @upload="uploadDocument"
      />

      <RecommendationsStep
        v-else
        :recommendations="global.recommendations"
        :submitted="financing.submitted"
        :status="global.application?.status || ''"
        :review-comment="global.application?.reviewComment"
        :events="global.application?.events || []"
        :offer-data="global.application?.offerData"
        @close="closeForm"
        @select="submitApplication"
        @offer-decision="decideOffer"
      />
    </template>
  </section>
</template>

<style lang="less" scoped src="./financing-wizard.less"></style>
