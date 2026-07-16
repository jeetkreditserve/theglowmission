"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type RitualItem = {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  description: string;
  image: string;
  image_url: string | null;
  image_alt: string;
  duration: string;
  session_count: number;
  currency: string;
  price_amount: string | null;
  sale_price_amount: string | null;
  discount_label: string;
  price_note: string;
  inclusions: string[];
  featured: boolean;
  cta_label: string;
  cta_url: string;
  calendly_event_url: string;
  active: boolean;
  ordering: number;
};

export default function AdminGlowRitualsPage() {
  return (
    <AdminShell title="Glow Rituals">
      <AdminResourceManager<RitualItem>
        path="/admin/services/"
        title="Glow ritual menu"
        itemLabel="ritual"
        createLabel="New ritual"
        defaults={{
          title: "",
          slug: "",
          short_description: "",
          description: "",
          image_alt: "",
          duration: "50 MINS",
          session_count: 1,
          currency: "INR",
          price_amount: null,
          sale_price_amount: null,
          discount_label: "",
          price_note: "",
          inclusions: [],
          featured: false,
          cta_label: "Book this ritual",
          cta_url: "/campaigns/glow-consultation",
          calendly_event_url: "",
          active: true,
          ordering: 0
        }}
        columns={[
          { label: "Ritual", value: (item) => item.title },
          { label: "Duration", value: (item) => item.duration },
          { label: "Price", value: (item) => `${item.currency} ${item.sale_price_amount || item.price_amount || "-"}` },
          { label: "Offer", value: (item) => item.discount_label || "-" },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") }
        ]}
        fields={[
          { name: "title", label: "Title", required: true },
          { name: "slug", label: "Slug" },
          { name: "short_description", label: "Short description", type: "textarea", span: "full", required: true },
          { name: "description", label: "Full description", type: "textarea", span: "full" },
          { name: "image", label: "Ritual image", type: "image", span: "full" },
          { name: "image_alt", label: "Image alt text", span: "full" },
          { name: "duration", label: "Duration" },
          { name: "session_count", label: "Session count", type: "number", required: true },
          { name: "currency", label: "Currency", required: true },
          { name: "price_amount", label: "Regular price", type: "number" },
          { name: "sale_price_amount", label: "Sale price", type: "number" },
          { name: "discount_label", label: "Discount label" },
          { name: "price_note", label: "Price note", span: "full" },
          { name: "inclusions", label: "Ritual flow", type: "jsonList", span: "full", help: "One flow step per line." },
          { name: "cta_label", label: "CTA label", required: true },
          { name: "cta_url", label: "CTA URL" },
          { name: "calendly_event_url", label: "Calendly event URL", span: "full" },
          { name: "featured", label: "Featured", type: "checkbox" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
        getPreviewHref={() => "/glow-rituals"}
      />
    </AdminShell>
  );
}
