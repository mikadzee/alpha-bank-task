<template>
  <div class="company-switcher">
    <div class="avatar">
      <img v-if="avatar" :src="avatar" alt="">
      <div v-else></div>
    </div>

    <div class="text">
      <h2>{{name}}</h2>
      <p>ИНН {{inn}}</p>
    </div>

    <button @click="null" class="more-btn">
      <SvgIcon icon="icon-arrow-botton" />
    </button>

    <div class="more">
      <!--      logika-->
    </div>
  </div>
</template>


<script setup lang="ts">

import SvgIcon from "~/components/shared/SvgIcon.vue";

defineProps<{
  avatar?: string;
  name: string;
  inn: number;
}>()
</script>

<style scoped lang="less" src="./company-switcher.less"></style>
