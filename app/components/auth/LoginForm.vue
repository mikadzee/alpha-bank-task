<template>
  <div class="auth-page">
    <AuthHeader link-text="Зарегистрироваться" link-to="/register" />
    <section class="auth-form">
      <div class="form-heading">
        <h1>Привет! Войдите<br>в личный кабинет</h1>
      </div>

      <form class="fields" novalidate @submit.prevent="submitLogin">
        <AppInput
          v-model="email"
          name="email"
          label="Электронная почта"
          type="email"
          autocomplete="email"
          inputmode="email"
          :error="errors.email"
          required
        />
        <AppInput
          v-model="password"
          name="password"
          label="Пароль"
          type="password"
          autocomplete="current-password"
          :error="errors.password"
          required
        />
        <AppButton
          class="submit-button"
          text="Вперед"
          type="submit"
          variant="dark"
        />
      </form>

      <p class="switch-form">
        Ещё нет аккаунта?
        <NuxtLink to="/register">Зарегистрироваться</NuxtLink>
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AuthHeader from "~/components/auth/AuthHeader.vue";
import AppButton from "~/components/shared/AppButton.vue";
import AppInput from "~/components/shared/AppInput.vue";
import { validateLoginForm, type AuthErrors } from "~/helpers/authValidation";

const email = ref("");
const password = ref("");
const errors = ref<AuthErrors>({});

function submitLogin() {
  errors.value = validateLoginForm(email.value, password.value);
  if (Object.keys(errors.value).length) return;

  // тута логика
}
</script>

<style lang="less" scoped src="./login-form.less"></style>
