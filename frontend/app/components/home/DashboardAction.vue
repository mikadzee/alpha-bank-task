<script setup lang="ts">
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import CheckerHelper from "~/components/shared/status/CheckerHelper.vue";
</script>
<template>
  <section class="dashboard">
    <CheckerHelper text="Финансовый навигатор" type="success"/>

    <div class="text">
      <h2>Подберем финансирование под ваши цели</h2>
      <p>Укажите цель, выручку и расходы. Демонстрационный помощник сравнит кредитные продукты, рассчитает примерный платёж и объяснит, как получилась рекомендация.</p>
    </div>

    <NuxtLink to="/financing?new=1">
      <span>
        Начать подбор финансирования
      </span>
      <SvgIcon icon="icon-arrow-right"/>
    </NuxtLink>
    <small class="demo-note">Предварительный расчёт на синтетических данных — не банковский скоринг и не решение о выдаче кредита.</small>
  </section>
</template>

<style lang="less" scoped src="./dashboard-action.less"></style>
