"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";
import { ExportLink } from "@/components/admin/AdminLists";

type Campaign = {
  id: number;
  title: string;
  slug: string;
  status: string;
  summary: string;
  offer_label: string;
  hero_image: string;
  hero_image_url: string | null;
  hero_image_alt: string;
  button_label: string;
  submitting_label: string;
  empty_select_label: string;
  checkbox_label: string;
  error_message: string;
  schedule_enabled: boolean;
  starts_at: string | null;
  ends_at: string | null;
  success_message: string;
  redirect_url: string;
  seo_title: string;
  seo_description: string;
  response_count: number;
  is_active_now: boolean;
};

export default function AdminCampaignsPage() {
  return (
    <AdminShell title="Campaigns">
      <AdminResourceManager<Campaign>
        path="/admin/campaign-forms/"
        title="Campaign forms"
        itemLabel="campaign"
        createLabel="New campaign"
        defaults={{
          title: "",
          slug: "",
          status: "draft",
          summary: "",
          offer_label: "",
          hero_image_alt: "",
          button_label: "Submit request",
          submitting_label: "Sending your request...",
          empty_select_label: "Choose a glow ritual",
          checkbox_label: "Yes",
          error_message: "Please check the highlighted fields and try again.",
          schedule_enabled: false,
          starts_at: null,
          ends_at: null,
          success_message: "Thank you. We will get back to you soon.",
          redirect_url: "",
          seo_title: "",
          seo_description: ""
        }}
        columns={[
          { label: "Title", value: (item) => item.title },
          { label: "Status", value: (item) => item.status },
          { label: "Offer", value: (item) => item.offer_label || "-" },
          { label: "Responses", value: (item) => item.response_count },
          { label: "Active now", value: (item) => (item.is_active_now ? "Yes" : "No") },
          { label: "Export", value: (item) => <ExportLink formId={item.id} /> }
        ]}
        fields={[
          { name: "title", label: "Title" },
          { name: "slug", label: "Slug" },
          {
            name: "status",
            label: "Status",
            type: "select",
            options: [
              { label: "Draft", value: "draft" },
              { label: "Published", value: "published" },
              { label: "Archived", value: "archived" }
            ]
          },
          { name: "offer_label", label: "Offer label" },
          { name: "summary", label: "Summary", type: "textarea", span: "full" },
          { name: "hero_image", label: "Hero image", type: "image", span: "full" },
          { name: "hero_image_alt", label: "Hero image alt text", span: "full" },
          { name: "button_label", label: "Submit button label" },
          { name: "submitting_label", label: "Submitting label" },
          { name: "empty_select_label", label: "Empty select label" },
          { name: "checkbox_label", label: "Checkbox label" },
          { name: "error_message", label: "Error message", type: "textarea", span: "full" },
          { name: "schedule_enabled", label: "Enable scheduling", type: "checkbox", span: "full", help: "Only turn this on when the campaign should accept responses within a date window." },
          { name: "starts_at", label: "Starts at", type: "datetime", help: "Optional unless scheduling is enabled." },
          { name: "ends_at", label: "Ends at", type: "datetime", help: "Optional unless scheduling is enabled." },
          { name: "success_message", label: "Success message", type: "textarea", span: "full" },
          { name: "redirect_url", label: "Redirect URL" },
          { name: "seo_title", label: "SEO title", span: "full" },
          { name: "seo_description", label: "SEO description", type: "textarea", span: "full" }
        ]}
        getEditHref={(item) => `/admin/campaigns/${item.id}/builder`}
        getPreviewHref={(item) => `/campaigns/${item.slug}`}
      />
    </AdminShell>
  );
}
