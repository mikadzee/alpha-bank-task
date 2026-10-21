<script setup lang="ts">
</script>
<template>
  <svg
      xmlns="http://www.w3.org/2000/svg"
      style="position: absolute; width: 0; height: 0; overflow: hidden"
  >
    <symbol id="icon-home" viewBox="0 0 24 24">
      <path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V10Z"/>
      <path d="M9 21v-8h6v8"/>
    </symbol>

    <!-- мои заявки -->
    <symbol id="icon-file-text" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/>
      <path d="M14 2v6h6"/>
      <path d="M8 13h8M8 17h6"/>
    </symbol>

    <!-- кредиты -->
    <symbol id="icon-credit-card" viewBox="0 0 24 24">
      <rect x="2" y="5" width="20" height="14" rx="3"/>
      <path d="M2 10h20M6 15h4"/>
    </symbol>

    <!-- Компания -->
    <symbol id="icon-building" viewBox="0 0 24 24">
      <rect x="3" y="2" width="18" height="20" rx="2"/>
      <path d="M9 22v-5h6v5"/>
      <path d="M7 6h2M15 6h2M7 10h2M15 10h2M7 14h2M15 14h2"/>
    </symbol>

    <!-- Документы -->
    <symbol id="icon-folder" viewBox="0 0 24 24">
      <path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>
      <path d="M3 11h18"/>
    </symbol>

    <!-- Обзор -->
    <symbol id="icon-dashboard" viewBox="0 0 24 24">
      <rect x="3" y="3" width="7" height="9" rx="1.5"/>
      <rect x="14" y="3" width="7" height="5" rx="1.5"/>
      <rect x="14" y="12" width="7" height="9" rx="1.5"/>
      <rect x="3" y="16" width="7" height="5" rx="1.5"/>
    </symbol>

    <!-- Заявки клиентов -->
    <symbol id="icon-clipboard" viewBox="0 0 24 24">
      <rect x="4" y="4" width="16" height="18" rx="2"/>
      <rect x="8" y="2" width="8" height="4" rx="1"/>
      <path d="M8 12h8M8 16h8"/>
    </symbol>

    <!-- Сотрудники / клиенты -->
    <symbol id="icon-users" viewBox="0 0 24 24">
      <circle cx="9" cy="8" r="3"/>
      <path d="M3 20v-2a6 6 0 0 1 12 0v2H3Z"/>
      <path d="M16 5a3 3 0 0 1 0 6M18 15a5 5 0 0 1 3 5"/>
    </symbol>

    <!-- Аналитика -->
    <symbol id="icon-chart" viewBox="0 0 24 24">
      <path d="M3 3v18h18"/>
      <path d="M7 17v-4M12 17V9M17 17V5"/>
    </symbol>

    <!-- Настройки -->
    <symbol id="icon-settings" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="3"/>
      <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
      <path d="m4.93 4.93 2.12 2.12m9.9 9.9 2.12 2.12M19.07 4.93l-2.12 2.12m-9.9 9.9-2.12 2.12"/>
    </symbol>
  </svg>
</template>

<style scoped>
.svg-sprite {
  position: absolute;
  width: 0;
  height: 0;
  overflow: hidden;
}
</style>