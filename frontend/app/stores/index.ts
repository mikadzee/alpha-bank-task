import axios, { type AxiosResponse } from "axios";
import { defineStore } from "pinia";
import { getAccessToken, getApiErrorMessage, isUnauthorized, setAccessToken } from "~/services/api";
import { serviceApplications } from "~/services/serviceApplications";
import { serviceCompanies, type CompanyRecord } from "~/services/serviceCompanies";
import { serviceAuth, type AuthUser } from "~/services/serviceAuth";
import { serviceStaff } from "~/services/serviceStaff";

type StaffApplication = {
  id: string,
  status: string,
  companyData?: Record<string, any>,
  financialData?: Record<string, any>,
  productName?: string,
  clientEmail?: string,
  submittedAt?: string
};

type StaffApplicationDetail = StaffApplication & {
  documents: Array<Record<string, any>>,
  assessment?: Record<string, any>,
  events?: Array<Record<string, any>>,
  offerData?: Record<string, any> | null,
  reviewComment?: string | null,
  reviewedAt?: string | null
};

type CompanyInfo = Omit<CompanyRecord, "id"> & {
  id?: string
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
  reasons: {
    title: string,
    description: string
  }[],
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
    companies: [] as CompanyInfo[],
    selectedCompanyId: "",
    companyLookupFound: null as boolean | null,
    applicationId: "",
    application: null as Application | null,
    applications: [] as Application[],
    recommendations: [] as Recommendation[],
    products: [] as Array<Record<string, any>>,
    feed: [] as Array<Record<string, any>>,
    staffApplications: [] as StaffApplication[],
    staffApplication: null as StaffApplicationDetail | null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken && state.user)
  },
  actions: {
    async request<T>(callback: () => Promise<AxiosResponse<T>>, canRefresh = true, showLoader = true): Promise<T> {
      if (showLoader) {
        this.pendingRequests += 1;
        this.loading = true;
      }

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
        if (showLoader) {
          this.pendingRequests -= 1;
          this.loading = this.pendingRequests > 0;
        }
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
      this.companies = [];
      this.selectedCompanyId = "";
      this.companyLookupFound = null;
      this.applicationId = "";
      this.application = null;
      this.applications = [];
      this.recommendations = [];
      this.staffApplications = [];
      this.staffApplication = null;
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
        if (this.user?.role === "client") {
          await this.loadApplications();
          await this.loadCompanies();
        }
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
        return;
      }

      if (this.user?.role === "client") {
        try {
          await this.loadApplications();
        } catch {
          this.error = "";
        }
        try {
          await this.loadCompanies();
        } catch {
          this.error = "";
        }
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

      const current = this.applications.find((item) => item.id === this.applicationId)
        || this.applications.find((item) => item.status === "draft")
        || this.applications[0];

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

    async loadProducts() {
      try {
        const result = await this.request(() => serviceApplications.products()) as Array<Record<string, any>> | { products?: Array<Record<string, any>> };
        this.products = Array.isArray(result) ? result : result.products || [];
        return this.products;
      } catch (error) {
        throw error;
      }
    },

    async loadBusinessFeed() {
      try {
        const result = await this.request(() => serviceApplications.feed()) as { items?: Array<Record<string, any>> };
        this.feed = result.items || [];
        return this.feed;
      } catch (error) {
        throw error;
      }
    },

    async downloadDocument(applicationId: string, documentId: string, fileName: string) {
      try {
        const blob = await this.request(() => serviceApplications.document(applicationId, documentId)) as Blob;
        if (import.meta.client) {
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = fileName || "document";
          link.click();
          URL.revokeObjectURL(url);
        }
      } catch (error) {
        throw error;
      }
    },

    async loadCompanies() {
      const result = await this.request(() => serviceCompanies.list());
      const response = result as CompanyInfo[] | { companies?: CompanyInfo[] };
      this.companies = Array.isArray(response) ? response : response.companies || [];

      const applicationInn = this.application?.companyData?.inn;
      const current = this.companies.find((item) => item.id === this.selectedCompanyId)
        || this.companies.find((item) => item.inn === applicationInn)
        || this.companies[0];

      this.selectedCompanyId = current?.id || "";
      this.company = current || (this.application?.companyData as CompanyInfo) || null;
      return this.companies;
    },

    async loadStaffApplications(status = "pending", search = "") {
      try {
        const result = await this.request(() => serviceStaff.applications(status, search)) as StaffApplication[];
        this.staffApplications = Array.isArray(result) ? result : [];
        return this.staffApplications;
      } catch (error) {
        throw error;
      }
    },

    async loadStaffApplication(id: string) {
      try {
        const result = await this.request(() => serviceStaff.application(id)) as StaffApplicationDetail;
        this.staffApplication = result;
        return result;
      } catch (error) {
        throw error;
      }
    },

    async downloadStaffDocument(applicationId: string, documentId: string) {
      try {
        return await this.request(() => serviceStaff.document(applicationId, documentId)) as Blob;
      } catch (error) {
        throw error;
      }
    },

    async decideStaffApplication(id: string, decision: "approved" | "rejected" | "needs_info" | "counteroffer", comment: string, proposal?: { proposedAmount: number, proposedTermMonths: number }) {
      try {
        const result = await this.request(() => serviceStaff.decide(id, decision, comment, proposal)) as StaffApplication;
        this.staffApplications = this.staffApplications.filter((item) => item.id !== id);
        if (this.staffApplication?.id === id) {
          this.staffApplication = { ...this.staffApplication, ...result };
        }
        return result;
      } catch (error) {
        throw error;
      }
    },

    selectCompany(id: string) {
      const company = this.companies.find((item) => item.id === id);

      if (company) {
        this.selectedCompanyId = company.id || "";
        this.company = company;
      }
    },

    async deleteCompany(id: string) {
      try {
        await this.request(() => serviceCompanies.delete(id));
        this.companies = this.companies.filter((item) => item.id !== id);

        if (this.selectedCompanyId === id) {
          const nextCompany = this.companies[0];
          this.selectedCompanyId = nextCompany?.id || "";
          this.company = nextCompany || null;
        }
      } catch (error) {
        throw error;
      }
    },

    updateApplicationList(application: Application) {
      this.applications = [application, ...this.applications.filter((item) => item.id !== application.id)];
    },

    async createApplication() {
      const result = await this.request(() => serviceApplications.create()) as Application;
      this.applicationId = result.id;
      this.application = result;
      this.recommendations = [];
      this.updateApplicationList(result);
      return result;
    },

    async ensureDraft() {
      const current = this.applications.find((item) => item.id === this.applicationId) || this.application;

      if (current?.id && ["draft", "needs_info"].includes(current.status || "")) {
        return current.id;
      }

      const result = await this.createApplication();
      return result.id;
    },

    async loadApplication(id: string) {
      const result = await this.request(() => serviceApplications.get(id)) as Application;
      this.application = result;
      this.applicationId = result.id;
      this.updateApplicationList(result);

      if (result.companyData) {
        const companyData = {
          inn: String(result.companyData.inn || ""),
          ogrn: String(result.companyData.ogrn || ""),
          companyName: result.companyData.companyName || "",
          address: result.companyData.address || "",
          okved: result.companyData.okved || ""
        };
        const savedCompany = this.companies.find((item) => item.inn === companyData.inn);
        this.company = savedCompany || companyData;

        if (savedCompany) {
          this.selectedCompanyId = savedCompany.id || "";
        }
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
          ogrn: /^(\d{13}|\d{15})$/.test(company.ogrn) ? company.ogrn : "",
          companyName: company.name,
          address: company.address,
          okved
        };

        const result = await this.request(() => serviceApplications.update(id, { companyData })) as Application;
        const savedCompany = await this.request(() => serviceCompanies.save(companyData));
        this.companies = [savedCompany, ...this.companies.filter((item) => item.id !== savedCompany.id && item.inn !== savedCompany.inn)];
        this.selectedCompanyId = savedCompany.id;
        this.company = savedCompany;
        this.application = result;
        this.updateApplicationList(result);
        return result;
      } catch (error) {
        throw error;
      }
    },

    async autosaveCompanyDraft(company: {
      inn: string,
      ogrn: string,
      name: string,
      address: string,
      activity: string,
      otherActivity: string
    }) {
      const companyData: Record<string, string> = {
        companyName: company.name,
        address: company.address,
        okved: company.activity === "other" ? company.otherActivity : company.activity
      };

      companyData.inn = company.inn;
      companyData.ogrn = company.ogrn;

      if (!companyData.inn && !companyData.companyName && !companyData.address && !companyData.okved) {
        return;
      }

      try {
        const id = await this.ensureDraft();
        const result = await this.request(() => serviceApplications.update(id, { companyData }), true, false) as Application;
        this.application = result;
        this.updateApplicationList(result);
        return result;
      } catch {
        this.error = "";
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
        this.updateApplicationList(result);
        return result;
      } catch (error) {
        throw error;
      }
    },

    async autosaveFinanceDraft(finance: {
      revenue: string,
      term: string,
      expenses: string,
      amount: string,
      purpose: string,
      details: string,
      otherPurpose: string
    }) {
      const toNumber = (value: string) => {
        const digits = value.replace(/\D/g, "");
        return digits ? Number(digits) : undefined;
      };
      const financialData: Record<string, string | number | null> = {};
      const revenue = toNumber(finance.revenue);
      const expenses = toNumber(finance.expenses);
      const amount = toNumber(finance.amount);
      const term = Number(finance.term.match(/\d+/)?.[0] || 0);
      const purposeMap: Record<string, string> = {
        "working-capital": "working_capital",
        expansion: "business_expansion"
      };

      financialData.annualRevenue = revenue ?? null;
      financialData.monthlyExpenses = expenses ?? null;
      financialData.requestedAmount = amount && amount > 0 ? amount : null;
      financialData.requestedTermMonths = term > 0 ? term : null;
      financialData.purpose = finance.purpose ? purposeMap[finance.purpose] || finance.purpose : null;
      financialData.purposeDetails = finance.purpose === "other" ? finance.otherPurpose || null : finance.details || null;

      if (!Object.keys(financialData).length) {
        return;
      }

      try {
        const id = await this.ensureDraft();
        const result = await this.request(() => serviceApplications.update(id, { financialData }), true, false) as Application;
        this.application = result;
        this.updateApplicationList(result);
        return result;
      } catch {
        this.error = "";
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
        this.updateApplicationList(result);
        return result;
      } catch (error) {
        throw error;
      }
    },

    async decideOffer(decision: "accept" | "decline") {
      const id = this.applicationId || this.application?.id;
      if (!id) throw new Error("Не удалось найти заявку");
      try {
        const result = await this.request(() => serviceApplications.offerDecision(id, decision)) as Application;
        this.application = result;
        this.updateApplicationList(result);
        return result;
      } catch (error) {
        throw error;
      }
    },

  }
});
