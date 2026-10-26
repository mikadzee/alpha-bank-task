<script setup lang="ts">
import CompanySwitcher from "~/components/layout/header/CompanySwitcher.vue";
import UserMenu from "~/components/layout/header/UserMenu.vue";
import { useGlobalStore } from "~/stores";

const store = useGlobalStore();

async function deleteCompany(id: string) {
  try {
    await store.deleteCompany(id);
  } catch {
    return;
  }
}
</script>

<template>
  <header class="app-header" :class="{ employee: store.user?.role === 'employee' }">
    <CompanySwitcher
      v-if="store.user?.role !== 'employee'"
      :name="store.company?.companyName || 'Моя компания'"
      :inn="store.company?.inn || '—'"
      :companies="store.companies"
      :selected-company-id="store.selectedCompanyId"
      @select="store.selectCompany"
      @delete="deleteCompany"
    />

    <UserMenu
      :name="store.user?.role === 'employee' ? 'Кредитный специалист' : store.user?.name || store.user?.email || 'Пользователь'"
      :type="store.user?.role === 'employee' ? 'Сотрудник банка' : 'Владелец бизнеса'"
    />
  </header>
</template>

<style lang="less" scoped src="./app-header.less"></style>
