<script setup lang="ts">
import { ref } from "vue";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import { useGlobalStore } from "~/stores";

defineProps<{
  avatar?: string;
  name: string;
  type: string;
}>();

const store = useGlobalStore();
const isOpen = ref(false);

async function logout() {
  await store.logout();
  await navigateTo("/login");
}
</script>

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
    <button type="button" class="more-btn" @click="isOpen = !isOpen">
      <SvgIcon icon="icon-arrow-botton" />
    </button>

    <div v-if="isOpen" class="more">
      <p>{{ store.user?.email }}</p>
      <button type="button" @click="logout">Выйти</button>
    </div>
  </div>
</template>

<style scoped lang="less" src="./user-menu.less"></style>
