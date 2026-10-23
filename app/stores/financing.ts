import { defineStore } from "pinia";

export type FinancingDocument = {
  id: string,
  type: "egrul_extract" | "accounting_report" | "tax_certificate" | "bank_statement" | "other",
  documentId: string,
  title: string,
  required: boolean,
  status: "success" | "error" | "empty",
  fileName: string,
  file: File | null
};

export const useFinancingStore = defineStore("financing", {
  state: () => ({
    step: 0,
    submitted: false,
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
        id: "egrul-extract",
        type: "egrul_extract",
        documentId: "",
        title: "Выписка из ЕГРЮЛ",
        required: true,
        status: "empty",
        fileName: "",
        file: null
      },
      {
        id: "accounting-report",
        type: "accounting_report",
        documentId: "",
        title: "Бухгалтерская отчетность",
        required: true,
        status: "empty",
        fileName: "",
        file: null
      },
      {
        id: "tax-certificate",
        type: "tax_certificate",
        documentId: "",
        title: "Справка о налоговой задолженности",
        required: true,
        status: "empty",
        fileName: "",
        file: null
      },
      {
        id: "bank-statement",
        type: "bank_statement",
        documentId: "",
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
      if (this.step < 3) {
        this.step += 1;
      }
    },
    addDocument() {
      this.documents.push({
        id: `extra-${Date.now()}`,
        type: "other",
        documentId: "",
        title: "Дополнительный документ",
        required: false,
        status: "empty",
        fileName: "",
        file: null
      });
    },
    setDocumentUploaded(id: string, file: File, documentId: string) {
      const document = this.documents.find((item) => item.id === id);

      if (document) {
        document.documentId = documentId;
        document.fileName = file.name;
        document.file = file;
        document.status = "success";
      }
    },
    setDocumentError(id: string) {
      const document = this.documents.find((item) => item.id === id);

      if (document) {
        document.status = "error";
      }
    },
    removeDocument(id: string) {
      const document = this.documents.find((item) => item.id === id);

      if (document) {
        document.documentId = "";
        document.fileName = "";
        document.file = null;
        document.status = "empty";
      }
    },
    setSubmitted() {
      this.submitted = true;
    }
  }
});
