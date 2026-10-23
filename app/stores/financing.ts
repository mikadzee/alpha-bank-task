import { defineStore } from "pinia";

export type FinancingDocument = {
  id: string,
  title: string,
  required: boolean,
  status: "success" | "error" | "empty",
  fileName: string,
  file: File | null
};

export const useFinancingStore = defineStore("financing", {
  state: () => ({
    step: 0,
    loading: false,
    company: {
      inn: "",
      ogrn: "",
      name: "",
      address: "",
      activity: "",
      otherActivity: ""
    },
    finance: {
      revenue: "",
      term: "24 месяца",
      expenses: "",
      amount: "",
      purpose: "",
      details: "",
      otherPurpose: ""
    },
    documents: [
      {
        id: "egrul",
        title: "Выписка из ЕГРЮЛ",
        required: true,
        status: "empty",
        fileName: "",
        file: null
      },
      {
        id: "accounting",
        title: "Бухгалтерская отчетность",
        required: true,
        status: "empty",
        fileName: "",
        file: null
      },
      {
        id: "tax-debt",
        title: "Справка о налоговой задолженности",
        required: true,
        status: "empty",
        fileName: "",
        file: null
      },
      {
        id: "bank-statement",
        title: "Выписка по расчетному счету",
        required: false,
        status: "empty",
        fileName: "",
        file: null
      }
    ] as FinancingDocument[]
  }),
  actions: {
    nextStep() {
      if (this.step < 2) {
        this.step += 1;
      }
    },
    addDocument() {
      this.documents.push({
        id: `extra-${Date.now()}`,
        title: "Дополнительный документ",
        required: false,
        status: "empty",
        fileName: "",
        file: null
      });
    },
    uploadDocument(id: string, file: File) {
      const document = this.documents.find((item) => item.id === id);

      if (document) {
        const supportedFormats = ["pdf", "jpg", "jpeg", "png", "doc", "docx", "xls", "xlsx"];
        const format = file.name.split(".").pop()?.toLowerCase();

        if (!format || !supportedFormats.includes(format)) {
          document.fileName = "";
          document.file = null;
          document.status = "error";
          return;
        }

        document.fileName = file.name;
        document.file = file;
        document.status = "success";
      }
    },
    apply() {
      console.log("Данные формы Pinia:", {
        company: { ...this.company },
        finance: { ...this.finance },
        documents: this.documents.map((document) => ({
          ...document,
          file: document.file ? {
            name: document.file.name,
            size: document.file.size,
            type: document.file.type
          } : null
        }))
      });

      this.step = 3;
      this.loading = true;

      // logika tyt
    }
  }
});
