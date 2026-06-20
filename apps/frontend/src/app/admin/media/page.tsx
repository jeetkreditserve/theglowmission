"use client";

import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type MediaItem = {
  id: number;
  title: string;
  file: string;
  file_url: string | null;
  alt_text: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export default function AdminMediaPage() {
  return (
    <AdminShell title="Media Library">
      <AdminResourceManager<MediaItem>
        path="/admin/media-assets/"
        title="Media assets"
        itemLabel="media asset"
        createLabel="Upload asset"
        defaults={{ title: "", alt_text: "", metadata: {} }}
        columns={[
          { label: "Title", value: (item) => item.title },
          { label: "Alt text", value: (item) => item.alt_text || "-" },
          { label: "Created", value: (item) => new Date(item.created_at).toLocaleString() }
        ]}
        fields={[
          { name: "title", label: "Title" },
          { name: "file", label: "File", type: "image", span: "full" },
          { name: "alt_text", label: "Alt text", span: "full" },
          { name: "metadata", label: "Metadata JSON", type: "json", span: "full" }
        ]}
        getPreviewHref={(item) => item.file_url || "/admin/media"}
      />
    </AdminShell>
  );
}
