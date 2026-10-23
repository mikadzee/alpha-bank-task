<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <GlobalLoader v-if="store.loading" />
  <SvgSprite />
</template>

<script setup lang="ts">
import SvgSprite from "~/components/shared/icons/SvgSprite.vue";
import GlobalLoader from "~/components/shared/loader/GlobalLoader.vue";
import { useGlobalStore } from "~/stores";

const store = useGlobalStore();
</script>


<style lang="less">
@import "./assets/styles/main.less";

</style>
