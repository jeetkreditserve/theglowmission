"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type ServiceItem = {
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
  active: boolean;
  ordering: number;
};

export default function AdminServicesPage() {
  return (
    <AdminShell title="Services">
      <AdminResourceManager<ServiceItem>
        path="/admin/services/"
        title="Treatment menu"
        itemLabel="service"
        createLabel="New treatment"
        defaults={{
          title: "",
          slug: "",
          short_description: "",
          description: "",
          image_alt: "",
          duration: "60 minutes",
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
          active: true,
          ordering: 0
        }}
        columns={[
          { label: "Treatment", value: (item) => item.title },
          { label: "Duration", value: (item) => item.duration },
          { label: "Price", value: (item) => `${item.currency} ${item.sale_price_amount || item.price_amount || "-"}` },
          { label: "Offer", value: (item) => item.discount_label || "-" },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") }
        ]}
        fields={[
          { name: "title", label: "Title" },
          { name: "slug", label: "Slug" },
          { name: "short_description", label: "Short description", type: "textarea", span: "full" },
          { name: "description", label: "Full description", type: "textarea", span: "full" },
          { name: "image", label: "Treatment image", type: "image", span: "full" },
          { name: "image_alt", label: "Image alt text", span: "full" },
          { name: "duration", label: "Duration" },
          { name: "session_count", label: "Session count", type: "number" },
          { name: "currency", label: "Currency" },
          { name: "price_amount", label: "Regular price", type: "number" },
          { name: "sale_price_amount", label: "Sale price", type: "number" },
          { name: "discount_label", label: "Discount label" },
          { name: "price_note", label: "Price note", span: "full" },
          { name: "inclusions", label: "Inclusions", type: "jsonList", span: "full", help: "One inclusion per line." },
          { name: "cta_label", label: "CTA label" },
          { name: "cta_url", label: "CTA URL" },
          { name: "featured", label: "Featured", type: "checkbox" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
        getPreviewHref={() => "/services"}
      />
    </AdminShell>
  );
}
