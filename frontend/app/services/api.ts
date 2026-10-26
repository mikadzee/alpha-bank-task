import axios, { type AxiosError } from "axios";

let accessToken = "";

export const api = axios.create({
  baseURL: "/api/v1",
  timeout: 20000,
  withCredentials: true
});

export function setAccessToken(token: string) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
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
