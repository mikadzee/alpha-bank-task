<script setup lang="ts">
</script>

<template>
  <div class="default-layout">
    <AsideApp/>

    <main class="content">
      <slot />
    </main>
  </div>
</template>

<style lang="less" scoped src="./default.less"></style>