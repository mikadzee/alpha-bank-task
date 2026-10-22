<template>
  <nav class="nav">
    <ul class="list">
      <li
          v-for="page in pages"
          :key="page.id"
          class="item"
      >
        <NuxtLink :to="page.path">
          <SvgIcon :icon="page.icon" />
          <span>{{ page.name }}</span>
        </NuxtLink>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { pages } from "~/constants/navigation";
import SvgIcon from "~/components/shared/SvgIcon.vue";
</script>

<style lang="less" scoped src="./navigation.less"></style>
