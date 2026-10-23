import { useGlobalStore } from "~/stores";

export default defineNuxtRouteMiddleware(async (to) => {
  // if (import.meta.server || to.path === "/login" || to.path === "/register") {
  //   return;
  // }
  //
  // const store = useGlobalStore();
  // await store.initialize();
  //
  // if (!store.isAuthenticated) {
  //   return navigateTo("/login");
  // }
});
