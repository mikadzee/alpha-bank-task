<template>
  <section class="credits-result">
    <div class="text">
      <h2>Подбор кредита</h2>
      <p>ИИ подобрала подходящие для вас варианты кредитования</p>
    </div>

    <div class="list">
      <div class="item">
        <CheckerHelper text="Рекомендуем" type="success"/>
        <h2 class="title">{{ }}</h2>

        <div class="fields">
          <div class="field">
            <div class="content">
              <p class="hint">Рекомендуемая сумма</p>
              <p class="text">{{ }}</p>
            </div>
            <div class="content">
              <p class="hint">Срок</p>
              <p class="text">{{ }}</p>
            </div>
          </div>

          <div class="field">
            <div class="content">
              <p class="hint">Ставка</p>
              <p class="text">{{ }}</p>
            </div>
            <div class="content">
              <p class="hint">Платёж в месяц</p>
              <p class="text">{{ }}</p>
            </div>
          </div>
        </div>

        <button>
          <span>
            Почему ИИ рекомендует этот кредит?
          </span>
          <SvgIcon icon="icon-arrow-bottom" />
        </button>

        <div class="more-ai">

        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import CheckerHelper from "~/components/shared/status/CheckerHelper.vue";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
</script>


<style lang="less" scoped src="./credits-result.less"></style>