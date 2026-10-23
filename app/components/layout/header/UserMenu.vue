<template>
  <div class="user-menu">
    <div class="avatar">
      <img v-if="avatar" :src="avatar" alt="">
      <div v-else></div>
    </div>

    <div class="text">
      <h2>{{name}}</h2>
      <p>{{type}}</p>
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
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";

defineProps<{
  avatar?: string;
  name: string;
  type: string;
}>()
</script>

<style scoped lang="less" src="./user-menu.less"></style>
