"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Eye, X } from "lucide-react";
import { CampaignActions } from "@/components/admin/CampaignActions";
import { AdminShell } from "@/components/admin/AdminShell";
import { adminFetch } from "@/lib/api";

type CampaignField = {
  id: number;
  label: string;
  key: string;
  field_type: string;
  ordering: number;
};

type CampaignFormDetail = {
  id: number;
  title: string;
  slug: string;
  fields: CampaignField[];
};

type ResponseItem = {
  id: number;
  submitted_at: string;
  response_data: Record<string, unknown>;
  metadata: Record<string, unknown>;
};

export default function CampaignResponsesPage() {
  const params = useParams<{ id: string }>();
  const formId = Number(params.id);
  const [form, setForm] = useState<CampaignFormDetail | null>(null);
  const [responses, setResponses] = useState<ResponseItem[]>([]);
  const [selected, setSelected] = useState<ResponseItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    Promise.all([
      adminFetch<CampaignFormDetail>(`/admin/campaign-forms/${formId}/`),
      adminFetch<ResponseItem[]>(`/admin/campaign-forms/${formId}/responses/`)
    ])
      .then(([formData, responseData]) => {
        if (!active) return;
        setForm(formData);
        setResponses(responseData);
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
  }, [formId]);

  const fields = useMemo(() => {
    return [...(form?.fields || [])].sort((left, right) => left.ordering - right.ordering || left.id - right.id);
  }, [form?.fields]);

  return (
    <AdminShell title="Campaign Responses">
      <div className="grid gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="font-display text-3xl text-espresso">{form?.title || "Responses"}</h2>
            <p className="mt-2 text-sm text-espresso/60">{responses.length} entries</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link href="/admin/campaign-responses" className="admin-icon-link">
              <ArrowLeft size={15} />
              All responses
            </Link>
            {form && <CampaignActions campaign={{ id: form.id, slug: form.slug }} compact />}
          </div>
        </div>

        {loading && <div className="border border-champagne/30 bg-ivory p-8 text-sm text-espresso/65">Loading responses...</div>}
        {error && <div className="border border-red-200 bg-red-50 p-8 text-sm text-red-700">{error}</div>}

        {!loading && !error && (
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
            <section className="overflow-hidden border border-champagne/30 bg-ivory">
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-left text-sm" style={{ minWidth: Math.max(760, 300 + fields.length * 170) }}>
                  <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                    <tr>
                      <th className="px-5 py-4 font-semibold">Submitted</th>
                      <th className="px-5 py-4 font-semibold">ID</th>
                      {fields.map((field) => (
                        <th key={field.id} className="px-5 py-4 font-semibold">
                          {field.label}
                        </th>
                      ))}
                      <th className="px-5 py-4 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {!responses.length && (
                      <tr>
                        <td className="px-5 py-8 text-espresso/55" colSpan={fields.length + 3}>
                          No responses found.
                        </td>
                      </tr>
                    )}
                    {responses.map((item) => (
                      <tr key={item.id} className="border-t border-champagne/20 align-top">
                        <td className="px-5 py-4 text-espresso/75">{new Date(item.submitted_at).toLocaleString()}</td>
                        <td className="px-5 py-4 font-semibold text-espresso">{item.id}</td>
                        {fields.map((field) => (
                          <td key={field.id} className="max-w-72 px-5 py-4 text-espresso/75">
                            <span className="line-clamp-3 whitespace-pre-wrap">{formatValue(item.response_data?.[field.key])}</span>
                          </td>
                        ))}
                        <td className="px-5 py-4">
                          <button type="button" className="admin-icon-link" onClick={() => setSelected(item)}>
                            <Eye size={15} />
                            Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <ResponseDetail response={selected} fields={fields} onClose={() => setSelected(null)} />
          </div>
        )}
      </div>
    </AdminShell>
  );
}

function ResponseDetail({ response, fields, onClose }: { response: ResponseItem | null; fields: CampaignField[]; onClose: () => void }) {
  if (!response) {
    return (
      <aside className="border border-champagne/25 bg-cream p-6 text-sm text-espresso/60">
        Select an entry to view the full response and metadata.
      </aside>
    );
  }

  return (
    <aside className="border border-champagne/25 bg-cream p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-display text-2xl text-espresso">Entry #{response.id}</h3>
          <p className="mt-1 text-sm text-espresso/60">{new Date(response.submitted_at).toLocaleString()}</p>
        </div>
        <button type="button" onClick={onClose} className="text-espresso/55 hover:text-espresso">
          <X size={20} />
        </button>
      </div>

      <div className="mt-6 grid gap-4">
        {fields.map((field) => (
          <div key={field.id} className="border-b border-champagne/25 pb-3">
            <div className="text-xs font-semibold uppercase tracking-[0.14em] text-espresso/50">{field.label}</div>
            <div className="mt-1 whitespace-pre-wrap text-sm text-espresso">{formatValue(response.response_data?.[field.key])}</div>
          </div>
        ))}
      </div>

      <div className="mt-6 border-t border-champagne/25 pt-5">
        <h4 className="text-xs font-semibold uppercase tracking-[0.14em] text-espresso/50">Metadata</h4>
        <dl className="mt-3 grid gap-3 text-sm">
          {Object.entries(response.metadata || {}).length ? (
            Object.entries(response.metadata).map(([key, value]) => (
              <div key={key}>
                <dt className="font-semibold text-espresso/65">{humanizeKey(key)}</dt>
                <dd className="mt-1 break-words text-espresso/75">{formatValue(value)}</dd>
              </div>
            ))
          ) : (
            <div className="text-espresso/55">No metadata recorded.</div>
          )}
        </dl>
      </div>
    </aside>
  );
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return value.length ? value.map(String).join(", ") : "-";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function humanizeKey(key: string) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
