<script setup lang="ts">
import FinancingProgress from "~/components/financing/Progress.vue";
import CompanyStep from "~/components/financing/CompanyStep.vue";
import FinanceStep from "~/components/financing/FinanceStep.vue";
import DocumentsStep from "~/components/financing/DocumentsStep.vue";
import ResultStep from "~/components/financing/ResultStep.vue";
import { useFinancingStore } from "~/stores/financing";

const store = useFinancingStore();

function closeForm() {
  navigateTo("/");
}
</script>

<template>
  <section class="financing">
    <FinancingProgress :step="store.step" />

    <CompanyStep
      v-if="store.step === 0"
      :company="store.company"
      @close="closeForm"
      @apply="store.nextStep"
    />

    <FinanceStep
      v-else-if="store.step === 1"
      :finance="store.finance"
      @close="closeForm"
      @apply="store.nextStep"
    />

    <DocumentsStep
      v-else-if="store.step === 2"
      :documents="store.documents"
      @close="closeForm"
      @apply="store.apply"
      @add="store.addDocument"
      @upload="store.uploadDocument"
    />

    <ResultStep v-else :loading="store.loading" />
  </section>
</template>

<style lang="less" scoped src="./financing-wizard.less"></style>
