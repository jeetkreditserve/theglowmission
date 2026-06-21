"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type GalleryItem = {
  id: number;
  title: string;
  alt_text: string;
  image: string;
  image_url: string | null;
  caption: string;
  active: boolean;
  ordering: number;
};

export default function AdminGalleryPage() {
  return (
    <AdminShell title="Gallery">
      <AdminResourceManager<GalleryItem>
        path="/admin/gallery/"
        title="Gallery images"
        itemLabel="gallery image"
        createLabel="New image"
        defaults={{ title: "", alt_text: "", caption: "", active: true, ordering: 0 }}
        columns={[
          { label: "Title", value: (item) => item.title },
          { label: "Caption", value: (item) => item.caption || "-" },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") },
          { label: "Order", value: (item) => item.ordering }
        ]}
        fields={[
          { name: "title", label: "Title", required: true },
          { name: "image", label: "Image", type: "image", span: "full" },
          { name: "alt_text", label: "Alt text", span: "full" },
          { name: "caption", label: "Caption", type: "textarea", span: "full" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
        getPreviewHref={() => "/gallery"}
      />
    </AdminShell>
  );
}
