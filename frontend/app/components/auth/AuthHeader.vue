<template>
  <header class="auth-header">
    <NuxtLink class="brand" to="/login">
      <img src="/images/logo/лого.png" alt="Альфа-Банк Бизнес">
    </NuxtLink>
    <NuxtLink class="auth-link" :to="props.linkTo">{{ props.linkText }}</NuxtLink>
  </header>
</template>

<script setup lang="ts">
const props = defineProps<{
  linkText: string,
  linkTo: string
}>();
</script>

<style lang="less" scoped src="./auth-header.less"></style>
