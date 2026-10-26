<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps<{
  loading: boolean
}>();

const visible = ref(false);
const showDelay = 300;
const minimumVisible = 450;
let shownAt = 0;
let showTimer: ReturnType<typeof setTimeout> | null = null;
let hideTimer: ReturnType<typeof setTimeout> | null = null;
let stopWatching: (() => void) | null = null;

function clearTimers() {
  if (showTimer) {
    clearTimeout(showTimer);
    showTimer = null;
  }

  if (hideTimer) {
    clearTimeout(hideTimer);
    hideTimer = null;
  }
}

onMounted(() => {
  stopWatching = watch(() => props.loading, (loading) => {
    clearTimers();

    if (loading) {
      showTimer = setTimeout(() => {
        visible.value = true;
        shownAt = Date.now();
      }, showDelay);
      return;
    }

    if (visible.value) {
      const visibleFor = Date.now() - shownAt;
      const hideDelay = Math.max(0, minimumVisible - visibleFor);

      hideTimer = setTimeout(() => {
        visible.value = false;
      }, hideDelay);
    }
  }, { immediate: true });
});

onBeforeUnmount(() => {
  clearTimers();
  stopWatching?.();
});
</script>

<template>
  <Transition name="loader-fade">
    <div v-if="visible" class="global-loader">
      <div class="loader-card">
        <div class="loader-mark"><span>А</span></div>
        <div class="loader-circle"></div>
        <p>Загружаем данные</p>
      </div>
    </div>
  </Transition>
</template>

<style lang="less" scoped src="./global-loader.less"></style>
