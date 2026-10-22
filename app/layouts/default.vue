<script setup lang="ts">
import AppSidebar from "~/components/layout/AppSidebar.vue";
import AppHeader from "~/components/layout/AppHeader.vue";
</script>

<template>
  <div class="default-layout">
    <AppSidebar />

    <main class="content">
      <AppHeader />
      <slot />
    </main>
  </div>
</template>

<style lang="less" scoped src="./default.less"></style>
