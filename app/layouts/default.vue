<script setup lang="ts">
import AppSidebar from "~/components/layout/AppSidebar.vue";
</script>

<template>
  <div class="default-layout">
    <AppSidebar />

    <main class="content">
      <slot />
    </main>
  </div>
</template>

<style lang="less" scoped src="./default.less"></style>
