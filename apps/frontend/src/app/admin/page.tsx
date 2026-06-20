"use client";

import Link from "next/link";
import { AdminShell } from "@/components/admin/AdminShell";
import { AdminTable, EditLink, ExportLink, PublicLink, useAdminList } from "@/components/admin/AdminLists";

type Campaign = { id: number; title: string; slug: string; status: string; response_count: number; is_active_now: boolean };
type Page = { id: number; title: string; slug: string; status: string; updated_at: string };
type Service = { id: number; title: string; active: boolean; duration: string };

export default function AdminDashboardPage() {
  const campaigns = useAdminList<Campaign>("/admin/campaign-forms/");
  const pages = useAdminList<Page>("/admin/pages/");
  const services = useAdminList<Service>("/admin/services/");

  return (
    <AdminShell title="Overview">
      <div className="grid gap-5 md:grid-cols-3">
        <Stat label="Pages" value={pages.items.length} />
        <Stat label="Services" value={services.items.length} />
        <Stat label="Campaigns" value={campaigns.items.length} />
      </div>
      <div className="mt-8 grid gap-8 xl:grid-cols-[1fr_0.9fr]">
        <AdminTable<Campaign>
          path="/admin/campaign-forms/"
          title="Recent campaigns"
          columns={[
            { label: "Title", value: (item) => item.title },
            { label: "Status", value: (item) => item.status },
            { label: "Responses", value: (item) => item.response_count }
          ]}
          action={(item) => (
            <div className="flex gap-4">
              <Link href={`/admin/campaigns/${item.id}/builder`} className="font-semibold">
                Builder
              </Link>
              <ExportLink formId={item.id} />
            </div>
          )}
        />
        <div className="border border-champagne/30 bg-ivory p-6">
          <h2 className="font-display text-2xl">Quick actions</h2>
          <div className="mt-6 grid gap-3">
            <EditLink href="/admin/theme" />
            <PublicLink href="/" />
            <Link href="/admin/campaigns" className="text-sm font-semibold text-espresso">
              Manage campaigns
            </Link>
          </div>
        </div>
      </div>
    </AdminShell>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-champagne/30 bg-ivory p-6">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-champagne">{label}</p>
      <p className="mt-4 font-display text-5xl text-espresso">{value}</p>
    </div>
  );
}

