<template>
  <svg class="icon">
    <use :href="'#' + props.icon" />
  </svg>
</template>

<script setup lang="ts">
  const props = defineProps<{
    icon: string,
    size?: number
  }>()
</script>

<style lang="less" scoped src="./svg-icon.less"></style>
