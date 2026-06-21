"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type HeroSlideItem = {
  id: number;
  title: string;
  subtitle: string;
  body: string;
  image: string;
  image_url: string | null;
  image_alt: string;
  offer_label: string;
  primary_cta_label: string;
  primary_cta_url: string;
  secondary_cta_label: string;
  secondary_cta_url: string;
  schedule_enabled: boolean;
  starts_at: string | null;
  ends_at: string | null;
  active: boolean;
  ordering: number;
};

export default function AdminHeroPage() {
  return (
    <AdminShell title="Hero Carousel">
      <AdminResourceManager<HeroSlideItem>
        path="/admin/hero-slides/"
        title="Homepage carousel slides"
        itemLabel="hero slide"
        createLabel="New slide"
        defaults={{
          title: "",
          subtitle: "",
          body: "",
          image_alt: "",
          offer_label: "",
          primary_cta_label: "Book a consultation",
          primary_cta_url: "/campaigns/glow-consultation",
          secondary_cta_label: "Explore rituals",
          secondary_cta_url: "/glow-rituals",
          schedule_enabled: false,
          starts_at: null,
          ends_at: null,
          active: true,
          ordering: 0
        }}
        columns={[
          { label: "Title", value: (item) => item.title },
          { label: "Offer", value: (item) => item.offer_label || "-" },
          { label: "Primary CTA", value: (item) => item.primary_cta_label },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") },
          { label: "Order", value: (item) => item.ordering }
        ]}
        fields={[
          { name: "title", label: "Title", span: "full", required: true },
          { name: "subtitle", label: "Subtitle", span: "full" },
          { name: "body", label: "Body", type: "textarea", span: "full" },
          { name: "image", label: "Hero image", type: "image", span: "full" },
          { name: "image_alt", label: "Image alt text", span: "full" },
          { name: "offer_label", label: "Offer label" },
          { name: "primary_cta_label", label: "Primary CTA label", required: true },
          { name: "primary_cta_url", label: "Primary CTA URL", required: true },
          { name: "secondary_cta_label", label: "Secondary CTA label" },
          { name: "secondary_cta_url", label: "Secondary CTA URL" },
          { name: "schedule_enabled", label: "Enable scheduling", type: "checkbox", span: "full", help: "Only turn this on when the slide should be shown within a date window." },
          { name: "starts_at", label: "Starts at", type: "datetime", help: "Optional unless scheduling is enabled." },
          { name: "ends_at", label: "Ends at", type: "datetime", help: "Optional unless scheduling is enabled." },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
        getPreviewHref={() => "/"}
      />
    </AdminShell>
  );
}
