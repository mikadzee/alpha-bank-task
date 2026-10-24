<script setup lang="ts">
import { onMounted } from "vue";
import FinancingProgress from "~/components/financing/Progress.vue";
import CompanyStep from "~/components/financing/CompanyStep.vue";
import FinanceStep from "~/components/financing/FinanceStep.vue";
import DocumentsStep from "~/components/financing/DocumentsStep.vue";
import RecommendationsStep from "~/components/financing/RecommendationsStep.vue";
import { useFinancingStore } from "~/stores/financing";
import { useGlobalStore } from "~/stores";

const financing = useFinancingStore();
const global = useGlobalStore();

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

  if (application.status && application.status !== "draft") {
    financing.submitted = true;
    financing.step = 3;
  } else if (documents.length) {
    financing.step = 2;
  } else if (finance.annualRevenue) {
    financing.step = 1;
  }
}

onMounted(async () => {
  if (global.applicationId) {
    try {
      await global.loadApplication(global.applicationId);
    } catch {
      return;
    }
  }

  restoreApplication();
});

function closeForm() {
  navigateTo("/");
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
  try {
    // await global.saveCompany(financing.company);
    financing.nextStep();
  } catch {
    return;
  }
}

async function saveFinance() {
  try {
    // await global.saveFinance(financing.finance);
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
    // await global.loadRecommendations();
    financing.nextStep();
  } catch {
    return;
  }
}

async function submitApplication(productId: string) {
  try {
    // await global.submitApplication(productId);
    financing.setSubmitted();
  } catch {
    return;
  }
}
</script>

<template>
  <section class="financing">
    <FinancingProgress :step="financing.step" />
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
      @close="closeForm"
      @select="submitApplication"
    />
  </section>
</template>

<style lang="less" scoped src="./financing-wizard.less"></style>
