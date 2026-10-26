import { api } from "./api";

export const serviceStaff = {
  applications: (status = "pending", search = "") =>
    api.get("/staff/applications", { params: { status, search } }),

  application: (id: string) =>
    api.get(`/staff/applications/${id}`),

  document: (applicationId: string, documentId: string) =>
    api.get(`/staff/applications/${applicationId}/documents/${documentId}`, { responseType: "blob" }),

  decide: (id: string, decision: "approved" | "rejected" | "needs_info" | "counteroffer", comment: string, proposal?: { proposedAmount: number, proposedTermMonths: number }) =>
    api.post(`/staff/applications/${id}/decision`, { decision, comment, ...proposal })
};
