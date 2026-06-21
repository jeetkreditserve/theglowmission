"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type TestimonialItem = {
  id: number;
  name: string;
  quote: string;
  role: string;
  is_anonymized: boolean;
  active: boolean;
  ordering: number;
};

export default function AdminTestimonialsPage() {
  return (
    <AdminShell title="Testimonials">
      <AdminResourceManager<TestimonialItem>
        path="/admin/testimonials/"
        title="Testimonials"
        itemLabel="testimonial"
        createLabel="New testimonial"
        defaults={{ name: "", quote: "", role: "", is_anonymized: true, active: true, ordering: 0 }}
        columns={[
          { label: "Name", value: (item) => item.name },
          { label: "Role", value: (item) => item.role || "-" },
          { label: "Anonymized", value: (item) => (item.is_anonymized ? "Yes" : "No") },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") },
          { label: "Order", value: (item) => item.ordering }
        ]}
        fields={[
          { name: "name", label: "Name", required: true },
          { name: "role", label: "Role" },
          { name: "quote", label: "Quote", type: "textarea", span: "full", required: true },
          { name: "is_anonymized", label: "Show as anonymized client note", type: "checkbox", span: "full" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
      />
    </AdminShell>
  );
}
