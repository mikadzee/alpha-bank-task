<template>
  <nav class="nav">
    <ul class="list">
      <li
          v-for="page in visiblePages"
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
import { computed } from "vue";
import { employeePages, pages } from "~/constants/navigation";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import { useGlobalStore } from "~/stores";

const store = useGlobalStore();
const visiblePages = computed(() => store.user?.role === "employee" ? employeePages : pages);
</script>

<style lang="less" scoped src="./navigation.less"></style>
