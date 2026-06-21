"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type NavigationItem = {
  id: number;
  label: string;
  url: string;
  placement: string;
  style: string;
  open_in_new_tab: boolean;
  active: boolean;
  ordering: number;
};

export default function AdminNavigationPage() {
  return (
    <AdminShell title="Navigation">
      <AdminResourceManager<NavigationItem>
        path="/admin/navigation-items/"
        title="Header and footer links"
        itemLabel="navigation item"
        createLabel="New link"
        defaults={{
          label: "",
          url: "",
          placement: "header",
          style: "link",
          open_in_new_tab: false,
          active: true,
          ordering: 0
        }}
        columns={[
          { label: "Label", value: (item) => item.label },
          { label: "URL", value: (item) => item.url },
          { label: "Placement", value: (item) => item.placement },
          { label: "Style", value: (item) => item.style },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") },
          { label: "Order", value: (item) => item.ordering }
        ]}
        fields={[
          { name: "label", label: "Label", required: true },
          { name: "url", label: "URL", required: true },
          {
            name: "placement",
            label: "Placement",
            type: "select",
            required: true,
            options: [
              { label: "Header navigation", value: "header" },
              { label: "Header CTA", value: "header_cta" },
              { label: "Footer navigation", value: "footer" },
              { label: "Footer CTA", value: "footer_cta" },
              { label: "Footer contact", value: "footer_contact" },
              { label: "Social link", value: "social" }
            ]
          },
          {
            name: "style",
            label: "Style",
            type: "select",
            required: true,
            options: [
              { label: "Link", value: "link" },
              { label: "Primary button", value: "primary" },
              { label: "Secondary button", value: "secondary" },
              { label: "Muted", value: "muted" }
            ]
          },
          { name: "open_in_new_tab", label: "Open in new tab", type: "checkbox" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
      />
    </AdminShell>
  );
}
