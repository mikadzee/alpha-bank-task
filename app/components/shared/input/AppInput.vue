<template>
  <div class="app-input" :class="{ 'app-input--focused': isFocused, 'app-input--filled': hasValue, 'app-input--error': Boolean(props.error), 'app-input--disabled': props.disabled, 'app-input--suffix': Boolean(props.suffix) }">
    <div class="field">
      <input
        :id="inputId"
        :name="props.name"
        :type="inputType"
        :value="props.modelValue"
        :maxlength="props.maxLength"
        :autocomplete="props.autocomplete"
        :required="props.required"
        :disabled="props.disabled"
        :inputmode="props.inputmode"
        @input="updateValue"
        @focus="isFocused = true"
        @blur="isFocused = false; emit('blur', $event)"
      >
      <span v-if="props.suffix && hasValue" class="suffix" :style="suffixStyle">{{ props.suffix }}</span>
      <label :for="inputId">{{ props.label }}</label>
      <button
        v-if="props.type === 'password'"
        class="visibility-button"
        type="button"
        @click="isPasswordVisible = !isPasswordVisible"
      >
        <svg v-if="isPasswordVisible" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 3l18 18" />
          <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
          <path d="M9.9 5.2A10.7 10.7 0 0 1 12 5c5.2 0 8.7 4.4 9.5 6-.3.7-1.2 2-2.6 3.3M6.2 6.2C4.2 7.5 3 9.6 2.5 11c.8 1.6 4.3 6 9.5 6 1.2 0 2.3-.2 3.3-.7" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
          <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" />
          <circle cx="12" cy="12" r="2.5" />
        </svg>
      </button>
    </div>
    <p v-if="props.error" class="error-message">{{ props.error }}</p>
    <p v-else-if="props.hint" class="hint-message">{{ props.hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = withDefaults(defineProps<{
  id?: string,
  name: string,
  label: string,
  modelValue: string,
  type?: "text" | "email" | "password" | "tel" | "number",
  autocomplete?: string,
  inputmode?: "text" | "email" | "numeric" | "decimal" | "tel" | "search" | "url",
  format?: "digits" | "amount",
  maxLength?: number,
  suffix?: string,
  error?: string,
  hint?: string,
  required?: boolean,
  disabled?: boolean
}>(), {
  type: "text",
  autocomplete: "off",
  required: false,
  disabled: false
});

const emit = defineEmits<{
  "update:modelValue": [value: string],
  blur: [event: FocusEvent]
}>();

const isFocused = ref(false);
const isPasswordVisible = ref(false);
const inputId = computed(() => props.id || props.name);
const hasValue = computed(() => props.modelValue.length > 0);
const inputType = computed(() => props.type === "password" && isPasswordVisible.value ? "text" : props.type);
const suffixStyle = computed(() => {
  const digits = props.modelValue.match(/\d/g)?.length || 0;
  const spaces = props.modelValue.match(/ /g)?.length || 0;

  return {
    left: `${18 + digits * 8.5 + spaces * 4.5 + 4}px`
  };
});

function updateValue(event: Event) {
  const input = event.target as HTMLInputElement;
  const cursor = input.selectionStart || 0;
  const digitsBeforeCursor = input.value.slice(0, cursor).replace(/\D/g, "").length;
  let value = input.value;

  if (props.format === "digits") {
    value = value.replace(/\D/g, "");

    if (props.maxLength) {
      value = value.slice(0, props.maxLength);
    }
  }

  if (props.format === "amount") {
    value = value.replace(/\D/g, "").replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  }

  emit("update:modelValue", value);
  input.value = value;

  if (props.format) {
    let nextCursor = 0;
    let digits = 0;

    while (nextCursor < value.length && digits < digitsBeforeCursor) {
      if (/\d/.test(value[nextCursor])) {
        digits += 1;
      }

      nextCursor += 1;
    }

    input.setSelectionRange(nextCursor, nextCursor);
  }
}
</script>

<style lang="less" scoped src="./app-input.less"></style>
