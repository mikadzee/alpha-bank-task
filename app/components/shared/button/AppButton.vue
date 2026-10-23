<template>
  <button
    class="app-button"
    :class="`app-button--${props.variant}`"
    :type="props.type"
    :disabled="props.disabled || props.loading"
  >
    <span v-if="props.loading" class="loader"></span>
    <span>{{ props.loading ? props.loadingText : props.text }}</span>
  </button>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  text: string,
  type?: "button" | "submit" | "reset",
  variant?: "primary" | "secondary" | "dark",
  loading?: boolean,
  loadingText?: string,
  disabled?: boolean
}>(), {
  type: "button",
  variant: "primary",
  loading: false,
  loadingText: "Подождите...",
  disabled: false
});
</script>

<style lang="less" scoped src="./app-button.less"></style>
