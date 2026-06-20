"use client";

import { useParams } from "next/navigation";
import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type SectionItem = {
  id: number;
  page: number;
  section_type: string;
  title: string;
  subtitle: string;
  body: string;
  media: string;
  media_url: string | null;
  cta_label: string;
  cta_url: string;
  ordering: number;
  active: boolean;
  config: Record<string, unknown>;
};

export default function AdminPageSectionsPage() {
  const params = useParams<{ id: string }>();
  const pageId = Number(params.id);

  return (
    <AdminShell title="Page Sections">
      <AdminResourceManager<SectionItem>
        path="/admin/page-sections/"
        queryKey={`page=${pageId}`}
        title="Page sections"
        itemLabel="section"
        createLabel="New section"
        defaults={{
          page: pageId,
          section_type: "rich_text",
          title: "",
          subtitle: "",
          body: "",
          cta_label: "",
          cta_url: "",
          ordering: 0,
          active: true,
          config: {}
        }}
        columns={[
          { label: "Type", value: (item) => item.section_type },
          { label: "Title", value: (item) => item.title || "-" },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") },
          { label: "Order", value: (item) => item.ordering }
        ]}
        fields={[
          {
            name: "section_type",
            label: "Section type",
            type: "select",
            options: [
              { label: "Hero", value: "hero" },
              { label: "Story", value: "story" },
              { label: "Services", value: "services" },
              { label: "Gallery", value: "gallery" },
              { label: "Testimonials", value: "testimonials" },
              { label: "FAQs", value: "faqs" },
              { label: "CTA", value: "cta" },
              { label: "Rich text", value: "rich_text" }
            ]
          },
          { name: "title", label: "Title", span: "full" },
          { name: "subtitle", label: "Subtitle", span: "full" },
          { name: "body", label: "Body", type: "textarea", span: "full" },
          { name: "media", label: "Section image", type: "image", span: "full" },
          { name: "cta_label", label: "CTA label" },
          { name: "cta_url", label: "CTA URL" },
          { name: "config", label: "Config JSON", type: "json", span: "full" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
        transformPayload={(payload) => ({ ...payload, page: pageId })}
      />
    </AdminShell>
  );
}
