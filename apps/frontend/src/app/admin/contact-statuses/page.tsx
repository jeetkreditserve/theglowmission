"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Pencil, Plus, RefreshCcw, Save, Trash2, X } from "lucide-react";
import { AdminShell } from "@/components/admin/AdminShell";
import { useAdminToast } from "@/components/admin/AdminToasts";
import { ApiError, adminFetch, flattenApiErrors, formatApiError } from "@/lib/api";
import type { ContactStatus } from "@/types/cms";

type DraftStatus = {
  name: string;
  slug: string;
  ordering: number;
  is_default: boolean;
};

const emptyDraft: DraftStatus = {
  name: "",
  slug: "",
  ordering: 0,
  is_default: false
};

export default function AdminContactStatusesPage() {
  const [statuses, setStatuses] = useState<ContactStatus[]>([]);
  const [draft, setDraft] = useState<DraftStatus | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [replacementByStatus, setReplacementByStatus] = useState<Record<number, string>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const toast = useAdminToast();

  async function load() {
    setLoading(true);
    setError("");
    try {
      setStatuses(await adminFetch<ContactStatus[]>("/admin/contact-statuses/"));
    } catch (err: unknown) {
      const message = err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load contact statuses.";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sortedStatuses = useMemo(() => {
    return [...statuses].sort((left, right) => left.ordering - right.ordering || left.name.localeCompare(right.name));
  }, [statuses]);

  function startCreate() {
    setDraft(emptyDraft);
    setEditingId(null);
    setFieldErrors({});
  }

  function startEdit(status: ContactStatus) {
    setDraft({
      name: status.name,
      slug: status.slug,
      ordering: status.ordering,
      is_default: status.is_default
    });
    setEditingId(status.id);
    setFieldErrors({});
  }

  function cancel() {
    setDraft(null);
    setEditingId(null);
    setFieldErrors({});
  }

  async function save() {
    if (!draft || saving) return;
    setSaving(true);
    setFieldErrors({});
    try {
      const path = editingId ? `/admin/contact-statuses/${editingId}/` : "/admin/contact-statuses/";
      const method = editingId ? "PATCH" : "POST";
      await adminFetch<ContactStatus>(path, {
        method,
        body: JSON.stringify(draft)
      });
      toast.success("Contact status saved.");
      cancel();
      await load();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setFieldErrors(flattenApiErrors(err.data));
        toast.error(formatApiError(err.data, "Unable to save status."));
      } else {
        toast.error(err instanceof Error ? err.message : "Unable to save status.");
      }
    } finally {
      setSaving(false);
    }
  }

  async function remove(status: ContactStatus) {
    const replacement = replacementByStatus[status.id];
    const needsReplacement = status.contact_count > 0 || status.is_default;
    if (needsReplacement && !replacement) {
      toast.error("Choose a replacement status before deleting.");
      return;
    }
    const confirmed = window.confirm(`Delete ${status.name}?`);
    if (!confirmed) return;
    try {
      if (needsReplacement) {
        await adminFetch(`/admin/contact-statuses/${status.id}/delete-with-replacement/`, {
          method: "POST",
          body: JSON.stringify({ replacement_status: replacement })
        });
      } else {
        await adminFetch(`/admin/contact-statuses/${status.id}/`, { method: "DELETE" });
      }
      toast.success("Contact status deleted.");
      await load();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Unable to delete status.");
    }
  }

  return (
    <AdminShell title="Contact Statuses">
      <div className="grid gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Link href="/admin/contacts" className="admin-icon-link w-fit">
              <ArrowLeft size={15} />
              Contacts
            </Link>
            <h2 className="mt-3 font-display text-3xl text-espresso">Lifecycle statuses</h2>
            <p className="mt-2 text-sm text-espresso/60">Statuses are used across the central Contacts list.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button type="button" className="admin-button-secondary" onClick={load}>
              <RefreshCcw size={16} />
              Refresh
            </button>
            <button type="button" className="admin-button" onClick={startCreate}>
              <Plus size={16} />
              New status
            </button>
          </div>
        </div>

        {draft && (
          <section className="admin-panel">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-champagne/20 pb-5">
              <h3 className="font-display text-2xl text-espresso">{editingId ? "Edit status" : "Create status"}</h3>
              <button type="button" onClick={cancel} className="text-espresso/55 hover:text-espresso">
                <X size={20} />
              </button>
            </div>
            <div className="mt-6 grid gap-5 md:grid-cols-2">
              <TextField label="Name" value={draft.name} error={fieldErrors.name} onChange={(value) => setDraft({ ...draft, name: value })} />
              <TextField label="Slug" value={draft.slug} error={fieldErrors.slug} onChange={(value) => setDraft({ ...draft, slug: value })} />
              <TextField label="Ordering" value={draft.ordering} error={fieldErrors.ordering} inputMode="numeric" onChange={(value) => setDraft({ ...draft, ordering: Number(value || 0) })} />
              <label className="flex items-center gap-3">
                <input type="checkbox" checked={draft.is_default} onChange={(event) => setDraft({ ...draft, is_default: event.target.checked })} className="h-5 w-5 accent-champagne" />
                <span className="text-sm font-semibold text-espresso/75">Default for new contacts</span>
              </label>
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <button type="button" disabled={saving} className="admin-button disabled:opacity-55" onClick={save}>
                <Save size={16} />
                {saving ? "Saving..." : "Save"}
              </button>
              <button type="button" className="admin-button-secondary" onClick={cancel}>
                Cancel
              </button>
            </div>
          </section>
        )}

        {loading && <div className="admin-panel text-sm text-espresso/65">Loading statuses...</div>}
        {error && <div className="border border-red-200 bg-red-50 p-8 text-sm text-red-700">{error}</div>}

        {!loading && !error && (
          <section className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[820px] border-collapse text-left text-sm">
                <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Status</th>
                    <th className="px-5 py-4 font-semibold">Slug</th>
                    <th className="px-5 py-4 font-semibold">Contacts</th>
                    <th className="px-5 py-4 font-semibold">Replacement on delete</th>
                    <th className="px-5 py-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedStatuses.map((status) => (
                    <tr key={status.id} className="border-t border-champagne/20 align-top">
                      <td className="px-5 py-4">
                        <span className="font-semibold text-espresso">{status.name}</span>
                        {status.is_default && <span className="ml-2 bg-sage/15 px-2 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-sage">Default</span>}
                      </td>
                      <td className="px-5 py-4 text-espresso/75">{status.slug}</td>
                      <td className="px-5 py-4 text-espresso/75">{status.contact_count}</td>
                      <td className="px-5 py-4">
                        <select
                          value={replacementByStatus[status.id] || ""}
                          onChange={(event) => setReplacementByStatus({ ...replacementByStatus, [status.id]: event.target.value })}
                          className="admin-input min-w-48"
                        >
                          <option value="">Choose replacement</option>
                          {sortedStatuses
                            .filter((candidate) => candidate.id !== status.id)
                            .map((candidate) => (
                              <option key={candidate.id} value={candidate.id}>
                                {candidate.name}
                              </option>
                            ))}
                        </select>
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex flex-wrap items-center gap-2">
                          <button type="button" className="admin-icon-link" onClick={() => startEdit(status)}>
                            <Pencil size={15} />
                            Edit
                          </button>
                          <button type="button" className="admin-icon-link text-red-700" onClick={() => remove(status)}>
                            <Trash2 size={15} />
                            Delete
                          </button>
                        </div>
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

function TextField({
  label,
  value,
  error,
  inputMode,
  onChange
}: {
  label: string;
  value: string | number;
  error?: string;
  inputMode?: "numeric";
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
