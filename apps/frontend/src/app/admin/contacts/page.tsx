"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Download, Plus, RefreshCcw, Save, Search, Tags, X } from "lucide-react";
import { AdminShell } from "@/components/admin/AdminShell";
import { useAdminToast } from "@/components/admin/AdminToasts";
import { ApiError, adminFetch, apiBaseUrl, authHeaders, flattenApiErrors, formatApiError } from "@/lib/api";
import { phoneInputValue } from "@/lib/formValidation";
import type { ContactSummary, ContactStatus } from "@/types/cms";

type ConsentFilter = "" | "true" | "false";
type NewContactDraft = {
  full_name: string;
  email: string;
  phone: string;
  address: string;
  status: number | null;
  marketing_consent: boolean;
};

const emptyContactDraft: NewContactDraft = {
  full_name: "",
  email: "",
  phone: "",
  address: "",
  status: null,
  marketing_consent: false
};

export default function AdminContactsPage() {
  const [contacts, setContacts] = useState<ContactSummary[]>([]);
  const [statuses, setStatuses] = useState<ContactStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusId, setStatusId] = useState("");
  const [consent, setConsent] = useState<ConsentFilter>("");
  const [draft, setDraft] = useState<NewContactDraft | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const toast = useAdminToast();

  const query = useMemo(() => buildContactQuery({ search, statusId, consent }), [search, statusId, consent]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [contactData, statusData] = await Promise.all([
        adminFetch<ContactSummary[]>(`/admin/contacts/${query}`),
        adminFetch<ContactStatus[]>("/admin/contact-statuses/")
      ]);
      setContacts(contactData);
      setStatuses(statusData);
    } catch (err: unknown) {
      const message = err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load contacts.";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  async function exportContacts() {
    const response = await fetch(`${apiBaseUrl()}/admin/contacts/export/${query}`, {
      headers: authHeaders()
    });
    if (!response.ok) {
      toast.error("Unable to export contacts.");
      return;
    }
    const blob = await response.blob();
    const href = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = filenameFromDisposition(response.headers.get("Content-Disposition")) || "contacts.xlsx";
    anchor.click();
    window.URL.revokeObjectURL(href);
    toast.success("Contacts exported.");
  }

  async function createContact() {
    if (!draft || saving) return;
    setSaving(true);
    setFieldErrors({});
    try {
      await adminFetch<ContactSummary>("/admin/contacts/", {
        method: "POST",
        body: JSON.stringify(draft)
      });
      setDraft(null);
      toast.success("Contact created.");
      await load();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setFieldErrors(flattenApiErrors(err.data));
        toast.error(formatApiError(err.data, "Unable to create contact."));
      } else {
        toast.error(err instanceof Error ? err.message : "Unable to create contact.");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <AdminShell title="Contacts">
      <div className="grid gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="font-display text-3xl text-espresso">Central contact list</h2>
            <p className="mt-2 text-sm text-espresso/60">{contacts.length} contacts matching the current filters</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link href="/admin/contact-statuses" className="admin-button-secondary">
              <Tags size={16} />
              Statuses
            </Link>
            <button type="button" className="admin-button-secondary" onClick={load}>
              <RefreshCcw size={16} />
              Refresh
            </button>
            <button type="button" className="admin-button-secondary" onClick={() => setDraft(emptyContactDraft)}>
              <Plus size={16} />
              New contact
            </button>
            <button type="button" className="admin-button" onClick={exportContacts}>
              <Download size={16} />
              Export XLSX
            </button>
          </div>
        </div>

        <section className="admin-panel">
          <div className="grid gap-4 lg:grid-cols-[minmax(260px,1fr)_220px_220px]">
            <label>
              <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Search</span>
              <span className="mt-2 flex items-center border border-champagne/35 bg-white/70 px-3">
                <Search size={16} className="text-espresso/45" />
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  className="w-full bg-transparent px-3 py-3 text-sm text-espresso outline-none"
                  placeholder="Name, email, phone, address"
                />
              </span>
            </label>
            <label>
              <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Status</span>
              <select value={statusId} onChange={(event) => setStatusId(event.target.value)} className="admin-input mt-2">
                <option value="">All statuses</option>
                {statuses.map((status) => (
                  <option key={status.id} value={status.id}>
                    {status.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Marketing consent</span>
              <select value={consent} onChange={(event) => setConsent(event.target.value as ConsentFilter)} className="admin-input mt-2">
                <option value="">All contacts</option>
                <option value="true">Opted in</option>
                <option value="false">Not opted in</option>
              </select>
            </label>
          </div>
        </section>

        {draft && (
          <section className="admin-panel">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-champagne/20 pb-5">
              <h3 className="font-display text-2xl text-espresso">Create contact</h3>
              <button type="button" onClick={() => setDraft(null)} className="text-espresso/55 hover:text-espresso">
                <X size={20} />
              </button>
            </div>
            <div className="mt-6 grid gap-5 md:grid-cols-2">
              <TextField label="Full name" value={draft.full_name} error={fieldErrors.full_name} onChange={(value) => setDraft({ ...draft, full_name: value })} />
              <TextField label="Email" value={draft.email} error={fieldErrors.email} inputMode="email" onChange={(value) => setDraft({ ...draft, email: value })} />
              <TextField
                label="Phone"
                value={draft.phone}
                error={fieldErrors.phone}
                inputMode="numeric"
                onChange={(value) => setDraft({ ...draft, phone: phoneInputValue(value).value })}
              />
              <label>
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Status</span>
                <select value={draft.status || ""} onChange={(event) => setDraft({ ...draft, status: event.target.value ? Number(event.target.value) : null })} className="admin-input mt-2">
                  <option value="">No status</option>
                  {statuses.map((status) => (
                    <option key={status.id} value={status.id}>
                      {status.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="md:col-span-2">
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Address</span>
                <textarea value={draft.address} onChange={(event) => setDraft({ ...draft, address: event.target.value })} className="admin-input mt-2 min-h-24" />
              </label>
              <label className="flex items-center gap-3">
                <input type="checkbox" checked={draft.marketing_consent} onChange={(event) => setDraft({ ...draft, marketing_consent: event.target.checked })} className="h-5 w-5 accent-champagne" />
                <span className="text-sm font-semibold text-espresso/75">Marketing consent</span>
              </label>
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <button type="button" disabled={saving} className="admin-button disabled:opacity-55" onClick={createContact}>
                <Save size={16} />
                {saving ? "Saving..." : "Create contact"}
              </button>
              <button type="button" className="admin-button-secondary" onClick={() => setDraft(null)}>
                Cancel
              </button>
            </div>
          </section>
        )}

        {loading && <div className="admin-panel text-sm text-espresso/65">Loading contacts...</div>}
        {error && <div className="border border-red-200 bg-red-50 p-8 text-sm text-red-700">{error}</div>}

        {!loading && !error && (
          <section className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[980px] border-collapse text-left text-sm">
                <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Contact</th>
                    <th className="px-5 py-4 font-semibold">Status</th>
                    <th className="px-5 py-4 font-semibold">Consent</th>
                    <th className="px-5 py-4 font-semibold">Email</th>
                    <th className="px-5 py-4 font-semibold">Phone</th>
                    <th className="px-5 py-4 font-semibold">Responses</th>
                    <th className="px-5 py-4 font-semibold">Last activity</th>
                    <th className="px-5 py-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {!contacts.length && (
                    <tr>
                      <td colSpan={8} className="px-5 py-8 text-espresso/55">
                        No contacts found.
                      </td>
                    </tr>
                  )}
                  {contacts.map((contact) => (
                    <tr key={contact.id} className="border-t border-champagne/20 align-top">
                      <td className="px-5 py-4">
                        <Link href={`/admin/contacts/${contact.id}`} className="font-semibold text-espresso underline underline-offset-4">
                          {contact.display_name}
                        </Link>
                      </td>
                      <td className="px-5 py-4 text-espresso/75">{contact.status_name || "-"}</td>
                      <td className="px-5 py-4 text-espresso/75">{contact.marketing_consent ? "Opted in" : "Not opted in"}</td>
                      <td className="px-5 py-4 text-espresso/75">{contact.email || "-"}</td>
                      <td className="px-5 py-4 text-espresso/75">{contact.phone || "-"}</td>
                      <td className="px-5 py-4 text-espresso/75">{contact.source_response_count}</td>
                      <td className="px-5 py-4 text-espresso/75">{formatDate(contact.last_activity_at)}</td>
                      <td className="px-5 py-4">
                        <Link href={`/admin/contacts/${contact.id}`} className="admin-icon-link">
                          Open
                          <ArrowRight size={15} />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>
    </AdminShell>
  );
}

function buildContactQuery({ search, statusId, consent }: { search: string; statusId: string; consent: ConsentFilter }) {
  const params = new URLSearchParams();
  if (search.trim()) params.set("search", search.trim());
  if (statusId) params.set("status", statusId);
  if (consent) params.set("marketing_consent", consent);
  const value = params.toString();
  return value ? `?${value}` : "";
}

function filenameFromDisposition(disposition: string | null) {
  if (!disposition) return "";
  const match = disposition.match(/filename="?([^";]+)"?/i);
  return match?.[1] || "";
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "-";
}

function TextField({
  label,
  value,
  error,
  inputMode,
  onChange
}: {
  label: string;
  value: string;
  error?: string;
  inputMode?: "email" | "numeric";
  onChange: (value: string) => void;
}) {
  return (
    <label>
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">{label}</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} inputMode={inputMode} className="admin-input mt-2" />
      {error && <span className="mt-2 block text-sm font-semibold text-red-700">{error}</span>}
    </label>
  );
}
