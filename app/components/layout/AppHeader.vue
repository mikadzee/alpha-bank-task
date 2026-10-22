<script setup lang="ts">
import CompanySwitcher from "~/components/layout/header/CompanySwitcher.vue";
import UserMenu from "~/components/layout/header/UserMenu.vue";
</script>

<template>
  <header class="app-header">
    <CompanySwitcher name="ООО “ТехноПлюс”" :inn="7701234567" />

    <UserMenu name="Данил Ягодов" type="Владелец бизнеса" />
  </header>
</template>

<style lang="less" scoped src="./app-header.less"></style>