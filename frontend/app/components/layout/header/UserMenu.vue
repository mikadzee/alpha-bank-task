<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import { useGlobalStore } from "~/stores";

defineProps<{
  avatar?: string;
  name: string;
  type: string;
}>();

const store = useGlobalStore();
const isOpen = ref(false);
const menuRoot = ref<HTMLElement | null>(null);

function closeOnOutsideClick(event: PointerEvent) {
  if (event.target instanceof Node && !menuRoot.value?.contains(event.target)) {
    isOpen.value = false;
  }
}

function closeOnEscape(event: KeyboardEvent) {
  if (event.key === "Escape") isOpen.value = false;
}

onMounted(() => {
  document.addEventListener("pointerdown", closeOnOutsideClick);
  document.addEventListener("keydown", closeOnEscape);
});

onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", closeOnOutsideClick);
  document.removeEventListener("keydown", closeOnEscape);
});

async function logout() {
  await store.logout();
  await navigateTo("/login");
}
</script>

<template>
  <div ref="menuRoot" class="user-menu">
    <button type="button" class="trigger" :aria-expanded="isOpen" @click="isOpen = !isOpen">
      <span class="avatar">
        <img v-if="avatar" :src="avatar" alt="">
        <span v-else></span>
      </span>

      <span class="text">
        <span class="name">{{ name }}</span>
        <span class="type">{{ type }}</span>
      </span>
      <SvgIcon icon="icon-arrow-bottom" :class="{ opened: isOpen }" />
    </button>

    <div v-if="isOpen" class="more">
      <p>{{ store.user?.email }}</p>
      <button type="button" @click="logout">Выйти</button>
    </div>
  </div>
</template>

<style scoped lang="less" src="./user-menu.less"></style>
