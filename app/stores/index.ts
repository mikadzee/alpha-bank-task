import axios, { type AxiosResponse } from "axios";
import { defineStore } from "pinia";
import { getAccessToken, getApiErrorMessage, isUnauthorized, setAccessToken } from "~/services/api";
import { serviceApplications } from "~/services/serviceApplications";
import { serviceAuth, type AuthUser } from "~/services/serviceAuth";

type CompanyInfo = {
  inn: string,
  ogrn: string,
  companyName: string,
  address: string,
  okved: string
};

type Recommendation = {
  productId: string,
  name: string,
  amount: number,
  termMonths: number,
  annualRate: number,
  monthlyPayment: number,
  totalPayment: number,
  recommended: boolean,
  reasons: string[],
  warnings: string[]
};

type Application = Record<string, any> & {
  id: string,
  status?: string,
  companyData?: Partial<CompanyInfo>
};

let refreshPromise: Promise<boolean> | null = null;

export const useGlobalStore = defineStore("global", {
  state: () => ({
    loading: false,
    pendingRequests: 0,
    error: "",
    initialized: false,
    accessToken: "",
    user: null as AuthUser | null,
    company: null as CompanyInfo | null,
    companyLookupFound: null as boolean | null,
    applicationId: "",
    application: null as Application | null,
    applications: [] as Application[],
    recommendations: [] as Recommendation[],
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken && state.user)
  },
  actions: {
    async request<T>(callback: () => Promise<AxiosResponse<T>>, canRefresh = true): Promise<T> {
      this.pendingRequests += 1;
      this.loading = true;

      try {
        try {
          const response = await callback();
          this.error = "";
          return response.data;
        } catch (error) {
          if (canRefresh && isUnauthorized(error)) {
            const refreshed = await this.refreshToken();

            if (refreshed) {
              try {
                const response = await callback();
                this.error = "";
                return response.data;
              } catch (retryError) {
                if (isUnauthorized(retryError)) {
                  this.clearSession();

                  if (import.meta.client) {
                    await navigateTo("/login");
                  }
                }

                this.error = getApiErrorMessage(retryError);
                throw retryError;
              }
            }

            this.clearSession();

            if (import.meta.client) {
              await navigateTo("/login");
            }
          }

          this.error = getApiErrorMessage(error);
          throw error;
        }
      } finally {
        this.pendingRequests -= 1;
        this.loading = this.pendingRequests > 0;
      }
    },

    async refreshToken() {
      if (refreshPromise) {
        return refreshPromise;
      }

      refreshPromise = (async () => {
        try {
          const result = await this.request(() => serviceAuth.refresh(), false);

          if (!result.accessToken) {
            throw new Error("Сервер не вернул access token");
          }

          this.accessToken = result.accessToken;
          setAccessToken(result.accessToken);

          if (result.user) {
            this.user = this.normalizeUser(result.user);
          }

          return true;
        } catch {
          this.clearSession();
          this.error = "";
          return false;
        } finally {
          refreshPromise = null;
        }
      })();

      return refreshPromise;
    },

    normalizeUser(user: AuthUser) {
      return {
        ...user,
        id: user.id || user.userId
      };
    },

    clearSession() {
      this.accessToken = "";
      this.user = null;
      this.company = null;
      this.companyLookupFound = null;
      this.applicationId = "";
      this.application = null;
      this.applications = [];
      this.recommendations = [];
      setAccessToken("");
    },

    async initialize() {
      if (this.initialized) {
        return;
      }

      this.accessToken = getAccessToken();

      try {
        if (!this.accessToken && !(await this.refreshToken())) {
          return;
        }

        await this.loadUser();
        await this.loadApplications();
      } catch {
        this.clearSession();
      } finally {
        this.initialized = true;
        this.error = "";
      }
    },

    async loadUser() {
      try {
        const user = await this.request(() => serviceAuth.getMe());
        this.user = this.normalizeUser(user);
        return this.user;
      } catch (error) {
        throw error;
      }
    },

    async register(body: {
      email: string,
      password: string,
      passwordConfirmation: string
    }) {
      const result = await this.request(() => serviceAuth.register(body), false);
      this.accessToken = result.accessToken;
      this.user = this.normalizeUser(result.user);
      setAccessToken(result.accessToken);
      this.initialized = true;
      await this.loadAfterAuth();
      return result;
    },

    async login(body: { email: string, password: string }) {
      const result = await this.request(() => serviceAuth.login(body), false);
      this.accessToken = result.accessToken;
      this.user = this.normalizeUser(result.user);
      setAccessToken(result.accessToken);
      this.initialized = true;
      await this.loadAfterAuth();
      return result;
    },

    async loadAfterAuth() {
      try {
        await this.loadUser();
      } catch {
        this.error = "";
      }

      try {
        await this.loadApplications();
      } catch {
        this.error = "";
      }
    },

    async logout() {
      try {
        if (this.accessToken) {
          await this.request(() => serviceAuth.logout(), false);
        }
      } catch {
        this.error = "";
      } finally {
        this.clearSession();
        this.initialized = true;
      }
    },

    async lookupCompany(inn: string) {
      if (!/^\d{10}$|^\d{12}$/.test(inn)) {
        this.companyLookupFound = null;
        return false;
      }

      try {
        const result = await this.request(() => serviceApplications.lookupCompany(inn));
        const response = result as { found?: boolean, company?: Record<string, any>, companyData?: Record<string, any>, data?: Record<string, any> } & Record<string, any>;
        const company = response.company || response.companyData || response.data || response;

        this.companyLookupFound = Boolean(response.found);

        if (response.found && company) {
          const okved = company.okved || "";
          const activity = ["28.99", "46.90", "82.99"].includes(okved) ? okved : okved ? "other" : "";
          this.company = {
            inn: String(company.inn || inn),
            ogrn: String(company.ogrn || ""),
            companyName: company.companyName || company.name || "",
            address: company.address || "",
            okved
          };

          this.company = { ...this.company, okved: activity === "other" ? okved : activity };
        }

        return this.companyLookupFound;
      } catch (error) {
        this.companyLookupFound = null;
        throw error;
      }
    },

    async loadApplications() {
      const result = await this.request(() => serviceApplications.list());
      const response = result as Application[] | { applications?: Application[] };
      this.applications = Array.isArray(response) ? response : response.applications || [];

      const current = this.applications.find((item) => item.status === "draft") || this.applications[0];

      if (current) {
        this.applicationId = current.id;
        this.application = current;

        if (current.companyData) {
          this.company = {
            inn: String(current.companyData.inn || ""),
            ogrn: String(current.companyData.ogrn || ""),
            companyName: current.companyData.companyName || "",
            address: current.companyData.address || "",
            okved: current.companyData.okved || ""
          };
        }
      }

      return this.applications;
    },

    async ensureDraft() {
      if (this.applicationId) {
        return this.applicationId;
      }

      const result = await this.request(() => serviceApplications.create()) as { id: string, status?: string };
      this.applicationId = result.id;
      this.application = { id: result.id, status: result.status || "draft" };
      return result.id;
    },

    async loadApplication(id: string) {
      const result = await this.request(() => serviceApplications.get(id)) as Application;
      this.application = result;
      this.applicationId = result.id;

      if (result.companyData) {
        this.company = {
          inn: String(result.companyData.inn || ""),
          ogrn: String(result.companyData.ogrn || ""),
          companyName: result.companyData.companyName || "",
          address: result.companyData.address || "",
          okved: result.companyData.okved || ""
        };
      }

      return result;
    },

    async saveCompany(company: {
      inn: string,
      ogrn: string,
      name: string,
      address: string,
      activity: string,
      otherActivity: string
    }) {
      try {
        const id = await this.ensureDraft();
        const okved = company.activity === "other" ? company.otherActivity : company.activity;
        const companyData = {
          inn: company.inn,
          ogrn: company.ogrn,
          companyName: company.name,
          address: company.address,
          okved
        };

        const result = await this.request(() => serviceApplications.update(id, { companyData })) as Application;
        this.company = { ...companyData };
        this.application = result;
        return result;
      } catch (error) {
        throw error;
      }
    },

    async saveFinance(finance: {
      revenue: string,
      term: string,
      expenses: string,
      amount: string,
      purpose: string,
      details: string,
      otherPurpose: string
    }) {
      try {
        const id = await this.ensureDraft();
        const purposeMap: Record<string, string> = {
          "working-capital": "working_capital",
          expansion: "business_expansion"
        };
        const financialData = {
          annualRevenue: Number(finance.revenue.replace(/\D/g, "")),
          monthlyExpenses: Number(finance.expenses.replace(/\D/g, "")),
          requestedAmount: Number(finance.amount.replace(/\D/g, "")),
          requestedTermMonths: Number(finance.term.match(/\d+/)?.[0] || 0),
          purpose: purposeMap[finance.purpose] || finance.purpose,
          purposeDetails: finance.purpose === "other" ? finance.otherPurpose : finance.details
        };

        const result = await this.request(() => serviceApplications.update(id, { financialData })) as Application;
        this.application = result;
        return result;
      } catch (error) {
        throw error;
      }
    },

    async loadRecommendations() {
      try {
        const id = await this.ensureDraft();
        const result = await this.request(() => serviceApplications.recommendations(id)) as {
          recommendations?: Recommendation[]
        } | Recommendation[];
        this.recommendations = Array.isArray(result) ? result : result.recommendations || [];
        return this.recommendations;
      } catch (error) {
        throw error;
      }
    },

    async uploadDocument(documentType: string, file: File) {
      try {
        if (file.size > 10 * 1024 * 1024) {
          throw new Error("Файл должен быть не больше 10 МБ");
        }

        const supportedFormats = ["pdf", "jpg", "jpeg", "png"];
        const format = file.name.split(".").pop()?.toLowerCase();

        if (!format || !supportedFormats.includes(format)) {
          throw new Error("Можно загрузить PDF, JPG или PNG");
        }

        const id = await this.ensureDraft();
        return await this.request(() => serviceApplications.uploadDocument(id, documentType, file));
      } catch (error) {
        if (!axios.isAxiosError(error)) {
          this.error = getApiErrorMessage(error);
        }

        throw error;
      }
    },

    async submitApplication(productId: string) {
      try {
        const id = await this.ensureDraft();
        const result = await this.request(() => serviceApplications.submit(id, productId)) as Application;
        this.application = result;
        return result;
      } catch (error) {
        throw error;
      }
    },

  }
});
