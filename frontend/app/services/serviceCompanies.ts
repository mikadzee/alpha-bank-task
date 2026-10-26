import { api } from "./api";

export type CompanyRecord = {
  id: string,
  inn: string,
  ogrn: string,
  companyName: string,
  address: string,
  okved: string
};

export const serviceCompanies = {
  list: () => api.get<CompanyRecord[]>("/companies"),

  save: (company: Omit<CompanyRecord, "id">) =>
    api.post<CompanyRecord>("/companies", company),

  delete: (id: string) => api.delete(`/companies/${id}`)
};
