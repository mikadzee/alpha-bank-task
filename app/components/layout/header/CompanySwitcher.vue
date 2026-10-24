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

    <button type="button" class="more-btn">
      <SvgIcon icon="icon-arrow-bottom" />
    </button>

    <div class="more">
      <!--      logika-->
    </div>
  </div>
</template>


<script setup lang="ts">

import SvgIcon from "~/components/shared/icons/SvgIcon.vue";

defineProps<{
  avatar?: string;
  name: string;
  inn: string | number;
}>()
</script>

<style scoped lang="less" src="./company-switcher.less"></style>
