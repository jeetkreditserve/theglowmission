"use client";

import Link from "next/link";
import { AdminShell } from "@/components/admin/AdminShell";
import { AdminTable, ExportLink, PublicLink } from "@/components/admin/AdminLists";

type Campaign = { id: number; title: string; slug: string; status: string; response_count: number; is_active_now: boolean };

export default function AdminCampaignsPage() {
  return (
    <AdminShell title="Campaigns">
      <AdminTable<Campaign>
        path="/admin/campaign-forms/"
        title="Campaign forms"
        columns={[
          { label: "Title", value: (item) => item.title },
          { label: "Slug", value: (item) => item.slug },
          { label: "Status", value: (item) => item.status },
          { label: "Responses", value: (item) => item.response_count },
          { label: "Active now", value: (item) => (item.is_active_now ? "Yes" : "No") }
        ]}
        action={(item) => (
          <div className="flex flex-wrap gap-4">
            <Link href={`/admin/campaigns/${item.id}/builder`} className="text-sm font-semibold">
              Builder
            </Link>
            <Link href={`/admin/campaigns/${item.id}/responses`} className="text-sm font-semibold">
              Responses
            </Link>
            <PublicLink href={`/campaigns/${item.slug}`} />
            <ExportLink formId={item.id} />
          </div>
        )}
      />
    </AdminShell>
  );
}

