import { api } from "~/services/api";

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();
  api.defaults.baseURL = config.public.apiBase;
});
