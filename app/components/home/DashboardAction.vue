<script setup lang="ts">
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import CheckerHelper from "~/components/shared/status/CheckerHelper.vue";
</script>
<template>
  <section class="dashboard">
    <CheckerHelper text="Финансовый навигатор" type="success"/>

    <div class="text">
      <h2>Подберем финансирование под ваши цели</h2>
      <p>Расскажите о своей задаче, и ИИ проанализирует ваш бизнес, подерёт пододящие кредиты и объяснит, как они
        помогут достичь ваших целей.</p>
    </div>

    <NuxtLink to="#">
      <span>
        Начать подбор финансирования
      </span>
      <SvgIcon icon="icon-arrow-right"/>
    </NuxtLink>
  </section>
</template>

<style lang="less" scoped src="./dashboard-action.less"></style>
