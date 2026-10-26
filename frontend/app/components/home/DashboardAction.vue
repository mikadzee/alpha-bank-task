<script setup lang="ts">
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import CheckerHelper from "~/components/shared/status/CheckerHelper.vue";
</script>
<template>
  <section class="dashboard">
    <CheckerHelper text="Финансовый навигатор" type="success"/>

    <div class="text">
      <h2>Подберем финансирование под ваши цели</h2>
      <p>Укажите цель, выручку и расходы. Система сравнит условия кредитных продуктов, рассчитает примерный платёж и покажет, как сформировалась рекомендация.</p>
    </div>

    <NuxtLink to="/financing?new=1">
      <span>
        Начать подбор финансирования
      </span>
      <SvgIcon icon="icon-arrow-right"/>
    </NuxtLink>
    <small class="demo-note">Предварительный расчёт на синтетических данных — не банковский скоринг и не решение о выдаче кредита.</small>

    <aside class="method-card" aria-label="Что учитывает подбор">
      <h3>Что учитывает подбор</h3>
      <p>Система сравнивает условия продуктов с параметрами вашей заявки:</p>
      <ul>
        <li>цель финансирования</li>
        <li>запрошенную сумму и срок</li>
        <li>расчётный ежемесячный платёж</li>
        <li>денежный поток после расходов</li>
      </ul>
    </aside>
  </section>
</template>

<style lang="less" scoped src="./dashboard-action.less"></style>
