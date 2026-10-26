import { useGlobalStore } from "~/stores";

export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) {
    return;
  }

  const store = useGlobalStore();
  await store.initialize();

  if (store.user?.role === "employee" && ["/login", "/register"].includes(to.path)) {
    return navigateTo("/staff");
  }

  if (to.path === "/login" || to.path === "/register") {
    return;
  }

  if (!store.isAuthenticated) {
    return navigateTo("/login");
  }

  if (store.user?.role === "employee" && !to.path.startsWith("/staff")) {
    return navigateTo("/staff");
  }

  if (store.user?.role === "client" && to.path.startsWith("/staff")) {
    return navigateTo("/");
  }
});
