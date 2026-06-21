"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Eye, X } from "lucide-react";
import { AdminShell } from "@/components/admin/AdminShell";
import { ExportLink } from "@/components/admin/AdminLists";
import { adminFetch } from "@/lib/api";

type ResponseField = {
  id: number;
  label: string;
  key: string;
  field_type: string;
  ordering: number;
};

type ResponseItem = {
  id: number;
  form: number;
  form_title: string;
  form_slug: string;
  submitted_at: string;
  response_data: Record<string, unknown>;
  metadata: Record<string, unknown>;
  field_snapshot: ResponseField[];
};

export default function AdminCampaignResponsesPage() {
  const [responses, setResponses] = useState<ResponseItem[]>([]);
  const [selected, setSelected] = useState<ResponseItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    adminFetch<ResponseItem[]>("/admin/campaign-responses/")
      .then((items) => {
        if (!active) return;
        setResponses(items);
        setSelected(items[0] || null);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load campaign responses.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const sortedResponses = useMemo(() => {
    return [...responses].sort((left, right) => new Date(right.submitted_at).getTime() - new Date(left.submitted_at).getTime());
  }, [responses]);

  return (
    <AdminShell title="Campaign Responses">
      <div className="grid gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="font-display text-3xl text-espresso">All campaign entries</h2>
            <p className="mt-2 text-sm text-espresso/60">{responses.length} total responses across all campaigns</p>
          </div>
        </div>

        {loading && <div className="admin-panel text-sm text-espresso/65">Loading responses...</div>}
        {error && <div className="border border-red-200 bg-red-50 p-8 text-sm text-red-700">{error}</div>}

        {!loading && !error && (
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
            <section className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
              <div className="border-b border-champagne/20 px-5 py-4">
                <h3 className="font-display text-2xl text-espresso">Response inbox</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[880px] border-collapse text-left text-sm">
                  <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                    <tr>
                      <th className="px-5 py-4 font-semibold">Submitted</th>
                      <th className="px-5 py-4 font-semibold">Campaign</th>
                      <th className="px-5 py-4 font-semibold">Name</th>
                      <th className="px-5 py-4 font-semibold">Email</th>
                      <th className="px-5 py-4 font-semibold">Phone</th>
                      <th className="px-5 py-4 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {!sortedResponses.length && (
                      <tr>
                        <td className="px-5 py-8 text-espresso/55" colSpan={6}>
                          No campaign responses found.
                        </td>
                      </tr>
                    )}
                    {sortedResponses.map((item) => (
                      <tr key={item.id} className="border-t border-champagne/20 align-top">
                        <td className="px-5 py-4 text-espresso/75">{new Date(item.submitted_at).toLocaleString()}</td>
                        <td className="px-5 py-4">
                          <Link href={`/admin/campaigns/${item.form}/responses`} className="font-semibold text-espresso underline underline-offset-4">
                            {item.form_title || `Campaign #${item.form}`}
                          </Link>
                        </td>
                        <td className="px-5 py-4 text-espresso/75">{valueFor(item, ["full_name", "name"])}</td>
                        <td className="px-5 py-4 text-espresso/75">{valueFor(item, ["email"])}</td>
                        <td className="px-5 py-4 text-espresso/75">{valueFor(item, ["phone"])}</td>
                        <td className="px-5 py-4">
                          <div className="flex flex-wrap items-center gap-2">
                            <button type="button" className="admin-icon-link" onClick={() => setSelected(item)}>
                              <Eye size={15} />
                              Details
                            </button>
                            <ExportLink formId={item.form} className="admin-icon-link" />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <ResponseDetail response={selected} onClose={() => setSelected(null)} />
          </div>
        )}
      </div>
    </AdminShell>
  );
}

function ResponseDetail({ response, onClose }: { response: ResponseItem | null; onClose: () => void }) {
  if (!response) {
    return <aside className="border border-champagne/25 bg-cream p-6 text-sm text-espresso/60">Select an entry to view full details.</aside>;
  }
  const fields = [...(response.field_snapshot || [])].sort((left, right) => left.ordering - right.ordering || left.id - right.id);

  return (
    <aside className="border border-champagne/25 bg-cream p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-display text-2xl text-espresso">Entry #{response.id}</h3>
          <p className="mt-1 text-sm text-espresso/60">{response.form_title}</p>
          <p className="mt-1 text-sm text-espresso/60">{new Date(response.submitted_at).toLocaleString()}</p>
        </div>
        <button type="button" onClick={onClose} className="text-espresso/55 hover:text-espresso">
          <X size={20} />
        </button>
      </div>

      <div className="mt-6 grid gap-4">
        {fields.map((field) => (
          <div key={`${field.id}-${field.key}`} className="border-b border-champagne/25 pb-3">
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-espresso/50">{field.label}</div>
            <div className="mt-1 whitespace-pre-wrap text-sm text-espresso">{formatValue(response.response_data?.[field.key])}</div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap gap-2 border-t border-champagne/25 pt-5">
        <Link href={`/admin/campaigns/${response.form}/responses`} className="admin-button-secondary">
          Campaign responses
        </Link>
        <Link href={`/campaigns/${response.form_slug}`} target="_blank" className="admin-button-secondary">
          Preview campaign
        </Link>
      </div>
    </aside>
  );
}

function valueFor(item: ResponseItem, keys: string[]) {
  for (const key of keys) {
    const value = item.response_data?.[key];
    if (value !== undefined && value !== null && value !== "") return formatValue(value);
  }
  return "-";
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return value.length ? value.map(String).join(", ") : "-";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}
