<script setup lang="ts">
import SvgIcon from "~/components/shared/icons/SvgIcon.vue";
import type { FinancingDocument } from "~/stores/financing";

defineProps<{
  documents: FinancingDocument[]
}>();

const emit = defineEmits<{
  close: [],
  apply: [],
  add: [],
  upload: [id: string, file: File]
}>();

function uploadFile(event: Event, id: string) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];

  if (file) {
    emit("upload", id, file);
  }

  input.value = "";
}
</script>

<template>
  <form class="card documents" @submit.prevent="emit('apply')">
    <button class="close" type="button" @click="emit('close')">×</button>

    <div class="heading">
      <h1>Загрузите документы</h1>
      <p>Загрузите необходимые документы для рассмотрения заявки</p>
    </div>

    <div class="list">
      <div v-for="document in documents" :key="document.id" class="item">
        <div class="file-icon">
          <SvgIcon icon="icon-file-text" />
        </div>

        <div class="info">
          <h2>{{ document.title }}</h2>
          <span class="badge" :class="{ optional: !document.required }">
            {{ document.required ? "Обязательно" : "По запросу" }}
          </span>
          <p v-if="document.fileName" class="file-name">{{ document.fileName }}</p>
        </div>

        <span v-if="document.status === 'success'" class="status success">
          <SvgIcon icon="icon-upload-success" />
        </span>
        <label v-else class="upload" :class="{ retry: document.status === 'error' }">
          <input type="file" accept=".pdf,.jpg,.jpeg,.png" @change="uploadFile($event, document.id)">
          <span v-if="document.status === 'empty'">Загрузить</span>
          <SvgIcon v-else icon="icon-upload-retry" />
        </label>
      </div>
    </div>

    <button class="add" type="button" @click="emit('add')">
      <span>+</span>
      Добавить дополнительный документ
    </button>

    <button class="apply" type="submit">Применить</button>
  </form>
</template>

<style lang="less" scoped src="./documents-step.less"></style>
