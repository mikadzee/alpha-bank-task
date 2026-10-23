<script setup lang="ts">
import CompanySwitcher from "~/components/layout/header/CompanySwitcher.vue";
import UserMenu from "~/components/layout/header/UserMenu.vue";
import { useGlobalStore } from "~/stores";

const store = useGlobalStore();
</script>

<template>
  <header class="app-header">
    <CompanySwitcher :name="store.company?.companyName || 'Моя компания'" :inn="store.company?.inn || '—'" />

    <UserMenu
      :name="store.user?.name || store.user?.email || 'Пользователь'"
      :type="store.user?.role === 'employee' ? 'Сотрудник банка' : 'Владелец бизнеса'"
    />
  </header>
</template>

<style lang="less" scoped src="./app-header.less"></style>
