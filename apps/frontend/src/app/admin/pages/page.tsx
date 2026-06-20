"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type PageItem = {
  id: number;
  title: string;
  slug: string;
  status: string;
  seo_title: string;
  seo_description: string;
  ordering: number;
};

export default function AdminPagesPage() {
  return (
    <AdminShell title="Pages">
      <AdminResourceManager<PageItem>
        path="/admin/pages/"
        title="Pages"
        itemLabel="page"
        createLabel="New page"
        defaults={{ title: "", slug: "", status: "draft", seo_title: "", seo_description: "", ordering: 0 }}
        columns={[
          { label: "Title", value: (item) => item.title },
          { label: "Slug", value: (item) => item.slug },
          { label: "Status", value: (item) => item.status },
          { label: "Order", value: (item) => item.ordering }
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
          { name: "ordering", label: "Order", type: "number" },
          { name: "seo_title", label: "SEO title", span: "full" },
          { name: "seo_description", label: "SEO description", type: "textarea", span: "full" }
        ]}
        getPreviewHref={(item) => (item.slug === "home" ? "/" : item.slug === "services" ? "/glow-rituals" : `/${item.slug}`)}
        getEditHref={(item) => `/admin/pages/${item.id}/sections`}
      />
    </AdminShell>
  );
}
