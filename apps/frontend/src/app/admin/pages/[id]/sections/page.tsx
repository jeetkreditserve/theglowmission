"use client";

import { useParams } from "next/navigation";
import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type SectionItem = {
  id: number;
  page: number;
  section_type: string;
  eyebrow: string;
  title: string;
  subtitle: string;
  body: string;
  media: string;
  media_url: string | null;
  media_alt: string;
  cta_label: string;
  cta_url: string;
  cta_style: string;
  secondary_cta_label: string;
  secondary_cta_url: string;
  secondary_cta_style: string;
  layout_variant: string;
  background_variant: string;
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
          eyebrow: "",
          title: "",
          subtitle: "",
          body: "",
          media_alt: "",
          cta_label: "",
          cta_url: "",
          cta_style: "",
          secondary_cta_label: "",
          secondary_cta_url: "",
          secondary_cta_style: "",
          layout_variant: "",
          background_variant: "",
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
            required: true,
            options: [
              { label: "Hero", value: "hero" },
              { label: "Story", value: "story" },
              { label: "Glow Rituals", value: "services" },
              { label: "Gallery", value: "gallery" },
              { label: "Testimonials", value: "testimonials" },
              { label: "FAQs", value: "faqs" },
              { label: "CTA", value: "cta" },
              { label: "Rich text", value: "rich_text" }
            ]
          },
          { name: "eyebrow", label: "Eyebrow / small label" },
          { name: "title", label: "Title", span: "full" },
          { name: "subtitle", label: "Subtitle", span: "full" },
          { name: "body", label: "Body", type: "textarea", span: "full" },
          { name: "media", label: "Section image", type: "image", span: "full" },
          { name: "media_alt", label: "Image alt text", span: "full" },
          { name: "cta_label", label: "CTA label" },
          { name: "cta_url", label: "CTA URL" },
          {
            name: "cta_style",
            label: "CTA style",
            type: "select",
            options: [
              { label: "Default", value: "" },
              { label: "Primary", value: "primary" },
              { label: "Secondary", value: "secondary" },
              { label: "Dark", value: "dark" }
            ]
          },
          { name: "secondary_cta_label", label: "Secondary CTA label" },
          { name: "secondary_cta_url", label: "Secondary CTA URL" },
          {
            name: "secondary_cta_style",
            label: "Secondary CTA style",
            type: "select",
            options: [
              { label: "Default", value: "" },
              { label: "Primary", value: "primary" },
              { label: "Secondary", value: "secondary" },
              { label: "Dark", value: "dark" }
            ]
          },
          { name: "layout_variant", label: "Layout variant", help: "Examples: contact_details, split, centered." },
          {
            name: "background_variant",
            label: "Background",
            type: "select",
            options: [
              { label: "Default", value: "" },
              { label: "Ivory", value: "ivory" },
              { label: "Cream", value: "cream" },
              { label: "Dark", value: "dark" }
            ]
          },
          { name: "config", label: "Advanced config JSON", type: "json", span: "full" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
        transformPayload={(payload) => ({ ...payload, page: pageId })}
      />
    </AdminShell>
  );
}
