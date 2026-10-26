<script setup lang="ts">
import ApplicationsList from "~/components/home/ApplicationsList.vue";
import { useGlobalStore } from "~/stores";

definePageMeta({ layout: "default" });
const store = useGlobalStore();

async function openApplication(id: string) {
  await navigateTo(`/financing?applicationId=${encodeURIComponent(id)}`);
}

async function createApplication() {
  await navigateTo("/financing?new=1");
}
</script>

<template>
  <section class="page-shell">
    <div class="page-intro">
      <span class="eyebrow">Кредитный кабинет</span>
      <h1>Мои заявки</h1>
      <p>Черновики сохраняются автоматически. Здесь собраны заявки всех ваших компаний.</p>
    </div>
    <ApplicationsList :applications="store.applications" @create="createApplication" @open="openApplication" />
  </section>
</template>

<style scoped>
.page-shell { display: grid; gap: 20px; }
.page-intro { padding: 8px 2px 0; }
.eyebrow { color: #ef3124; font-size: 13px; font-weight: 600; }
h1 { margin: 7px 0; color: #171717; font-size: clamp(25px, 3vw, 34px); }
p { margin: 0; color: #777; font-size: 15px; }
</style>
