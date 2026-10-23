<script setup lang="ts">
defineProps<{
  loading: boolean
}>();
</script>

<template>
  <section class="card result">
    <div v-if="loading" class="content">
      <span class="loader"></span>
      <h1>Подбираем финансирование</h1>
      <p>Анализируем данные компании и ищем подходящие предложения</p>
    </div>

    <!-- // logika tyt -->
  </section>
</template>

<style lang="less" scoped src="./result-step.less"></style>
