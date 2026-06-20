"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type FAQItem = {
  id: number;
  question: string;
  answer: string;
  active: boolean;
  ordering: number;
};

export default function AdminFAQsPage() {
  return (
    <AdminShell title="FAQs">
      <AdminResourceManager<FAQItem>
        path="/admin/faqs/"
        title="FAQs"
        itemLabel="FAQ"
        createLabel="New FAQ"
        defaults={{ question: "", answer: "", active: true, ordering: 0 }}
        columns={[
          { label: "Question", value: (item) => item.question },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") },
          { label: "Order", value: (item) => item.ordering }
        ]}
        fields={[
          { name: "question", label: "Question", span: "full" },
          { name: "answer", label: "Answer", type: "textarea", span: "full" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
      />
    </AdminShell>
  );
}
