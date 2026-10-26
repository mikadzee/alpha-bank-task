<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";

type Company = {
  id: string,
  inn: string,
  companyName: string,
  ogrn: string,
  address: string,
  okved: string
};

const props = defineProps<{
  avatar?: string,
  name: string,
  inn: string | number,
  companies: Company[],
  selectedCompanyId: string
}>();

const emit = defineEmits<{
  select: [id: string],
  delete: [id: string]
}>();

const opened = ref(false);
const switcherRoot = ref<HTMLElement | null>(null);

function closeOnOutsideClick(event: PointerEvent) {
  if (event.target instanceof Node && !switcherRoot.value?.contains(event.target)) {
    opened.value = false;
  }
}

function closeOnEscape(event: KeyboardEvent) {
  if (event.key === "Escape") opened.value = false;
}

onMounted(() => {
  document.addEventListener("pointerdown", closeOnOutsideClick);
  document.addEventListener("keydown", closeOnEscape);
});

onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", closeOnOutsideClick);
  document.removeEventListener("keydown", closeOnEscape);
});
</script>

<template>
  <div ref="switcherRoot" class="company-switcher">
    <button class="current" type="button" @click="opened = !opened">
      <div class="avatar">
        <img v-if="props.avatar" :src="props.avatar" alt="">
        <div v-else></div>
      </div>

      <div class="text">
        <h2>{{ props.name }}</h2>
        <p>ИНН {{ props.inn }}</p>
      </div>

      <SvgIcon icon="icon-arrow-bottom" :class="{ opened }" />
    </button>

    <div v-if="opened" class="more">
      <div class="more-heading">
        <h3>Мои компании</h3>
        <span>{{ props.companies.length }}</span>
      </div>

      <p v-if="!props.companies.length" class="empty">Сохранённые компании появятся здесь после заполнения заявки</p>

      <div v-for="company in props.companies" :key="company.id" class="company-item">
        <button class="company-info" type="button" @click="emit('select', company.id); opened = false">
          <b>{{ company.companyName }}</b>
          <small>ИНН {{ company.inn }}</small>
          <span v-if="company.id === props.selectedCompanyId" class="selected">Выбрана</span>
        </button>
        <button class="delete" type="button" @click="emit('delete', company.id)">×</button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="less" src="./company-switcher.less"></style>
