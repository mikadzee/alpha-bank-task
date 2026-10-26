<script setup lang="ts">
import { onMounted } from "vue";
import { useGlobalStore } from "~/stores";

definePageMeta({ layout: "default" });
const store = useGlobalStore();
onMounted(async () => {
  if (!store.products.length) {
    try { await store.loadProducts(); } catch { /* The global API error is shown by the app shell. */ }
  }
});
const money = (value: number) => new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(value);
</script>

<template>
  <section class="loans-page">
    <header class="page-heading">
      <span class="eyebrow">Каталог</span>
      <h1>Кредитные продукты</h1>
      <p>Выберите направление, чтобы рассчитать подходящие условия для вашей компании.</p>
    </header>
    <div v-if="store.products.length" class="products-grid">
      <article v-for="product in store.products" :key="product.id" class="product-card">
        <span class="product-mark">А</span>
        <h2>{{ product.name }}</h2>
        <p>{{ product.description }}</p>
        <dl>
          <div><dt>Сумма</dt><dd>{{ money(product.minAmount) }} — {{ money(product.maxAmount) }}</dd></div>
          <div><dt>Срок</dt><dd>{{ product.minTermMonths }}–{{ product.maxTermMonths }} месяцев</dd></div>
          <div><dt>Демо-ставка</dt><dd>от {{ product.annualRate }}% годовых</dd></div>
        </dl>
        <NuxtLink class="primary" to="/financing?new=1">Рассчитать условия</NuxtLink>
      </article>
    </div>
    <div v-else-if="store.error" class="empty">Не удалось получить каталог. Попробуйте открыть страницу позже.</div>
    <p class="disclaimer">Каталог и ставки демонстрационные и не являются публичной офертой или решением банка.</p>
  </section>
</template>

<style scoped>
.loans-page { display: grid; gap: 22px; }
.page-heading { padding-top: 8px; }
.eyebrow { color: #ef3124; font-size: 13px; font-weight: 600; }
h1 { margin: 7px 0; color: #171717; font-size: clamp(25px, 3vw, 34px); }
.page-heading p,.product-card p { color: #777; }
.products-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(min(100%,320px),1fr)); gap: 16px; }
.product-card { display: flex; flex-direction: column; align-items: flex-start; gap: 14px; padding: 24px; border: 1px solid #e7e7e7; border-radius: 20px; background: white; }
.product-mark { display: grid; place-items: center; width: 42px; height: 42px; border-radius: 13px; color: white; background: #ef3124; font-weight: 700; }
.product-card h2 { margin: 0; font-size: 20px; }
.product-card p { margin: 0; line-height: 1.5; }
dl { display: grid; width: 100%; gap: 12px; margin: 4px 0; }
dl div { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid #eee; padding-bottom: 9px; }
dt { color: #777; } dd { margin: 0; font-weight: 600; text-align: right; }
.primary { margin-top: auto; padding: 13px 18px; border-radius: 12px; color: white; background: #ef3124; text-decoration: none; font-weight: 600; }
.disclaimer,.empty { color: #888; font-size: 13px; }
@media(max-width:560px) { dl div { flex-direction: column; gap: 4px; } dd { text-align: left; } }
</style>
