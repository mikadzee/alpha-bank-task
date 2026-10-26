<template>
  <div class="auth-page">
    <AuthHeader link-text="Войти" link-to="/login" />
    <section class="auth-form">
      <div class="form-heading">
        <h1>Создать аккаунт</h1>
        <p>Зарегистрируйтесь, чтобы заполнить заявку на финансирование</p>
      </div>

      <form class="fields" novalidate @submit.prevent="submitRegistration">
        <AppInput
          v-model="email"
          name="registration-email"
          label="Электронная почта"
          type="email"
          autocomplete="email"
          inputmode="email"
          :error="errors.email"
          required
        />
        <AppInput
          v-model="password"
          name="registration-password"
          label="Пароль"
          type="password"
          autocomplete="new-password"
          hint="Не менее 8 символов"
          :error="errors.password"
          required
        />
        <AppInput
          v-model="passwordConfirmation"
          name="password-confirmation"
          label="Повторите пароль"
          type="password"
          autocomplete="new-password"
          :error="errors.passwordConfirmation"
          required
        />
        <AppButton
          class="submit-button"
          text="Зарегистрироваться"
          type="submit"
          variant="dark"
          :loading="store.loading"
        />
      </form>

      <p v-if="store.error" class="request-error">{{ store.error }}</p>

      <p class="switch-form">
        Уже есть аккаунт?
        <NuxtLink to="/login">Войти</NuxtLink>
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AuthHeader from "~/components/auth/AuthHeader.vue";
import AppButton from "~/components/shared/button/AppButton.vue";
import AppInput from "~/components/shared/input/AppInput.vue";
import { validateRegistrationForm, type AuthErrors } from "~/helpers/authValidation";
import { useGlobalStore } from "~/stores";

const email = ref("");
const password = ref("");
const passwordConfirmation = ref("");
const errors = ref<AuthErrors>({});
const store = useGlobalStore();

async function submitRegistration() {
  errors.value = validateRegistrationForm(email.value, password.value, passwordConfirmation.value);
  if (Object.keys(errors.value).length) return;

  try {
    await store.register({
      email: email.value,
      password: password.value,
      passwordConfirmation: passwordConfirmation.value
    });
    await navigateTo("/");
  } catch {
    return;
  }
}
</script>

<style lang="less" scoped src="./register-form.less"></style>
