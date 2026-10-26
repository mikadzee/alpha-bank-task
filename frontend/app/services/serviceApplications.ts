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

  products: () => api.get("/products"),

  feed: () => api.get("/feed"),

  document: (applicationId: string, documentId: string) =>
    api.get(`/applications/${applicationId}/documents/${documentId}`, { responseType: "blob" }),

  uploadDocument: (id: string, documentType: string, file: File) => {
    const body = new FormData();
    body.append("documentType", documentType);
    body.append("file", file);

    return api.post(`/applications/${id}/documents`, body);
  },

  submit: (id: string, productId: string) =>
    api.post(`/applications/${id}/submit`, { productId }),

  offerDecision: (id: string, decision: "accept" | "decline") =>
    api.post(`/applications/${id}/offer-decision`, { decision })
};
