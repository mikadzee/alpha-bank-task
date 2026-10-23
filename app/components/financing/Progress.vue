<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  step: number
}>();

const steps = ["Компания", "Финансы", "Документация", "Подбор"];
const progress = computed(() => `${Math.min(((props.step + 1) / (steps.length - 1)) * 100, 100)}%`);
</script>

<template>
  <div class="progress">
    <div class="steps">
      <div class="track" :style="{ background: `linear-gradient(to right, #EF3124 0%, #EF3124 ${progress}, #E8E8E8 ${progress}, #E8E8E8 100%)` }"></div>

      <div v-for="(name, index) in steps" :key="name" class="item" :class="{ active: index <= props.step }">
        <span class="point"><i></i></span>
        <span class="name">{{ name }}</span>
      </div>
    </div>
  </div>
</template>

<style lang="less" scoped src="./progress.less"></style>
