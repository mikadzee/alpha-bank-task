<template>
  <div class="checker-helper" :class="props.type">
    <p>{{ props.text }}</p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  type: "success" | "error" | "pending",
  text: string
}>()
</script>

<style lang="less" scoped src="./checker-helper.less"></style>
