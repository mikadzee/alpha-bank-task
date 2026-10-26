<script setup lang="ts">
import { onMounted } from "vue";
import DashboardAction from "~/components/home/DashboardAction.vue";
import ApplicationsList from "~/components/home/ApplicationsList.vue";
import { useGlobalStore } from "~/stores";

const store = useGlobalStore();

onMounted(async () => {
  try { await store.loadBusinessFeed(); } catch { /* The dashboard remains usable if the optional feed is unavailable. */ }
});

function createApplication() {
  navigateTo("/financing?new=1");
}

function openApplication(id: string) {
  navigateTo(`/financing?applicationId=${id}`);
}

</script>
<template>
  <div class="home">
    <DashboardAction />
    <ApplicationsList
      :applications="store.applications"
      @create="createApplication"
      @open="openApplication"
    />
    <section v-if="store.feed.length" class="business-feed">
      <header><div><span>Персонально для вас</span><h2>Подсказки и события</h2></div></header>
      <article v-for="item in store.feed" :key="item.id" class="feed-item" :class="item.kind">
        <span class="feed-dot" aria-hidden="true"></span>
        <div><b>{{ item.title }}</b><p>{{ item.description }}</p><small v-if="item.companyName">Для {{ item.companyName }}</small></div>
      </article>
      <p class="feed-caption">Лента строится по сохранённым данным кабинета. Это демонстрационные подсказки, не внешние новости.</p>
    </section>
  </div>
</template>

<style scoped>
.home { display: grid; gap: 20px; }
.business-feed { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 12px; padding: 22px; border: 1px solid #e9e9e9; border-radius: 20px; background: #fff; }
.business-feed header { grid-column: 1 / -1; }
.business-feed header span { color: #ef3124; font-size: 12px; font-weight: 600; }
.business-feed h2 { margin: 4px 0 8px; color: #171717; font-size: 20px; }
.feed-item { display: flex; align-items: flex-start; gap: 10px; padding: 15px; border-radius: 14px; background: #f5f6f7; }
.feed-dot { width: 9px; height: 9px; flex: 0 0 auto; margin-top: 5px; border-radius: 50%; background: #ef3124; }
.feed-item.application .feed-dot { background: #08a66a; }
.feed-item.notice .feed-dot { background: #92979d; }
.feed-item b { color: #222; font-size: 14px; }
.feed-item p { margin: 5px 0; color: #666; font-size: 13px; line-height: 1.45; }
.feed-item small,.feed-caption { color: #888; font-size: 11px; }
.feed-caption { grid-column: 1 / -1; margin: 0; }
@media(max-width:900px) { .business-feed { grid-template-columns: 1fr; } }
</style>
