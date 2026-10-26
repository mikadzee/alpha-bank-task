import { api } from "./api";

export type AuthUser = {
  id?: string,
  userId?: string,
  email: string,
  role: "client" | "employee",
  name?: string,
  companyName?: string
};

export type AuthResponse = {
  accessToken: string,
  user: AuthUser
};

export const serviceAuth = {
  register: (body: {
    email: string,
    password: string,
    passwordConfirmation: string
  }) => api.post<AuthResponse>("/auth/register", body),

  login: (body: {
    email: string,
    password: string
  }) => api.post<AuthResponse>("/auth/login", body),

  getMe: () => api.get<AuthUser>("/auth/me"),

  // Backend TZ не описывает refresh/logout: эти маршруты фронт ожидает с HttpOnly refresh cookie.
  refresh: () => api.post<{ accessToken: string, user?: AuthUser }>("/auth/refresh"),

  logout: () => api.post("/auth/logout")
};
