import { api } from "./api";

export const serviceApplications = {
  lookupCompany: (inn: string) =>
    api.get(`/companies/lookup`, { params: { inn } }),

  create: () => api.post("/applications"),

  list: () => api.get("/applications"),

  get: (id: string) => api.get(`/applications/${id}`),

  update: (id: string, body: Record<string, unknown>) =>
    api.patch(`/applications/${id}`, body),

  recommendations: (id: string) =>
    api.get(`/applications/${id}/recommendations`),

  uploadDocument: (id: string, documentType: string, file: File) => {
    const body = new FormData();
    body.append("documentType", documentType);
    body.append("file", file);

    return api.post(`/applications/${id}/documents`, body);
  },

  submit: (id: string, productId: string) =>
    api.post(`/applications/${id}/submit`, { productId })
};
