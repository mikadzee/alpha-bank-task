import axios, { type AxiosError } from "axios";

const accessTokenKey = "alpha-bank-access-token";

export const api = axios.create({
  baseURL: "/api/v1",
  timeout: 20000,
  withCredentials: true
});

export function setAccessToken(token: string) {
  if (!import.meta.client) {
    return;
  }

  if (token) {
    sessionStorage.setItem(accessTokenKey, token);
  } else {
    sessionStorage.removeItem(accessTokenKey);
  }
}

export function getAccessToken() {
  if (!import.meta.client) {
    return "";
  }

  return sessionStorage.getItem(accessTokenKey) || "";
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

type ApiErrorResponse = {
  error?: {
    code?: string,
    message?: string,
    fields?: Record<string, string>
  }
};

export function getApiErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;

    return axiosError.response?.data?.error?.message || "Ошибка соединения с сервером";
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Неизвестная ошибка";
}

export function isUnauthorized(error: unknown) {
  return axios.isAxiosError(error) && error.response?.status === 401;
}
