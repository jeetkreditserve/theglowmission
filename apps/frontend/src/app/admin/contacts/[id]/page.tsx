"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, FileText, Merge, RefreshCcw, Save } from "lucide-react";
import { AdminShell } from "@/components/admin/AdminShell";
import { useAdminToast } from "@/components/admin/AdminToasts";
import { ApiError, adminFetch, flattenApiErrors, formatApiError } from "@/lib/api";
import { phoneInputValue } from "@/lib/formValidation";
import type { Contact, ContactStatus } from "@/types/cms";

type ResponseItem = {
  id: number;
  form: number;
  form_title: string;
  form_slug: string;
  submitted_at: string;
  response_data: Record<string, unknown>;
  contact_sync_status: string;
  contact_sync_error: string;
};

type DraftContact = Pick<
  Contact,
  "full_name" | "email" | "phone" | "address" | "age" | "skin_type" | "preferred_ritual" | "preferred_day" | "skin_goal" | "marketing_consent" | "status"
>;

export default function AdminContactDetailPage() {
  const params = useParams<{ id: string }>();
  const contactId = Number(params.id);
  const [contact, setContact] = useState<Contact | null>(null);
  const [draft, setDraft] = useState<DraftContact | null>(null);
  const [statuses, setStatuses] = useState<ContactStatus[]>([]);
  const [responses, setResponses] = useState<ResponseItem[]>([]);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [noteBody, setNoteBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const toast = useAdminToast();

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [contactData, statusData, responseData] = await Promise.all([
        adminFetch<Contact>(`/admin/contacts/${contactId}/`),
        adminFetch<ContactStatus[]>("/admin/contact-statuses/"),
        adminFetch<ResponseItem[]>(`/admin/campaign-responses/?contact=${contactId}`)
      ]);
      setContact(contactData);
      setDraft(toDraft(contactData));
      setStatuses(statusData);
      setResponses(responseData);
      setFieldErrors({});
    } catch (err: unknown) {
      const message = err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load contact.";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [contactId]);

  const sortedResponses = useMemo(() => {
    return [...responses].sort((left, right) => new Date(right.submitted_at).getTime() - new Date(left.submitted_at).getTime());
  }, [responses]);

  async function saveContact() {
    if (!draft || saving) return;
    setSaving(true);
    setFieldErrors({});
    try {
      const payload = {
        ...draft,
        age: draft.age === null || draft.age === undefined || String(draft.age) === "" ? null : Number(draft.age)
      };
      const updated = await adminFetch<Contact>(`/admin/contacts/${contactId}/`, {
        method: "PATCH",
        body: JSON.stringify(payload)
      });
      setContact(updated);
      setDraft(toDraft(updated));
      toast.success("Contact saved.");
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setFieldErrors(flattenApiErrors(err.data));
        toast.error(formatApiError(err.data, "Unable to save contact."));
      } else {
        toast.error(err instanceof Error ? err.message : "Unable to save contact.");
      }
    } finally {
      setSaving(false);
    }
  }

  async function addNote() {
    if (!noteBody.trim()) return;
    try {
      await adminFetch("/admin/contact-notes/", {
        method: "POST",
        body: JSON.stringify({ contact: contactId, body: noteBody.trim() })
      });
      setNoteBody("");
      toast.success("Note added.");
      await load();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Unable to add note.");
    }
  }

  async function mergeDuplicate(sourceId: number) {
    const confirmed = window.confirm(`Merge contact #${sourceId} into this contact?`);
    if (!confirmed) return;
    try {
      const updated = await adminFetch<Contact>(`/admin/contacts/${contactId}/merge/`, {
        method: "POST",
        body: JSON.stringify({ source_contact: sourceId })
      });
      setContact(updated);
      setDraft(toDraft(updated));
      toast.success("Contacts merged.");
      await load();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Unable to merge contacts.");
    }
  }

  return (
    <AdminShell title="Contact Profile">
      <div className="grid gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Link href="/admin/contacts" className="admin-icon-link w-fit">
              <ArrowLeft size={15} />
              Contacts
            </Link>
            <h2 className="mt-3 font-display text-3xl text-espresso">{contact?.display_name || "Contact"}</h2>
            {contact && <p className="mt-2 text-sm text-espresso/60">Created {formatDate(contact.created_at)} · Last activity {formatDate(contact.last_activity_at)}</p>}
          </div>
          <button type="button" className="admin-button-secondary" onClick={load}>
            <RefreshCcw size={16} />
            Refresh
          </button>
        </div>

        {loading && <div className="admin-panel text-sm text-espresso/65">Loading contact...</div>}
        {error && <div className="border border-red-200 bg-red-50 p-8 text-sm text-red-700">{error}</div>}

        {!loading && !error && contact && draft && (
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_390px]">
            <div className="grid gap-6">
              <section className="admin-panel">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-champagne/20 pb-5">
                  <h3 className="font-display text-2xl text-espresso">Contact details</h3>
                  <button type="button" disabled={saving} className="admin-button disabled:opacity-55" onClick={saveContact}>
                    <Save size={16} />
                    {saving ? "Saving..." : "Save"}
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
                    {fieldErrors.status && <span className="mt-2 block text-sm font-semibold text-red-700">{fieldErrors.status}</span>}
                  </label>
                  <label className="md:col-span-2">
                    <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Address</span>
                    <textarea value={draft.address} onChange={(event) => setDraft({ ...draft, address: event.target.value })} className="admin-input mt-2 min-h-24" />
                    {fieldErrors.address && <span className="mt-2 block text-sm font-semibold text-red-700">{fieldErrors.address}</span>}
                  </label>
                  <TextField label="Age" value={draft.age ?? ""} error={fieldErrors.age} inputMode="numeric" onChange={(value) => setDraft({ ...draft, age: value === "" ? null : Number(value) })} />
                  <TextField label="Skin type" value={draft.skin_type} error={fieldErrors.skin_type} onChange={(value) => setDraft({ ...draft, skin_type: value })} />
                  <TextField label="Preferred ritual" value={draft.preferred_ritual} error={fieldErrors.preferred_ritual} onChange={(value) => setDraft({ ...draft, preferred_ritual: value })} />
                  <TextField label="Preferred day" value={draft.preferred_day} error={fieldErrors.preferred_day} onChange={(value) => setDraft({ ...draft, preferred_day: value })} />
                  <label className="md:col-span-2">
                    <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Skin goal</span>
                    <textarea value={draft.skin_goal} onChange={(event) => setDraft({ ...draft, skin_goal: event.target.value })} className="admin-input mt-2 min-h-28" />
                  </label>
                  <label className="flex items-center gap-3">
                    <input type="checkbox" checked={draft.marketing_consent} onChange={(event) => setDraft({ ...draft, marketing_consent: event.target.checked })} className="h-5 w-5 accent-champagne" />
                    <span className="text-sm font-semibold text-espresso/75">Marketing consent</span>
                  </label>
                </div>
              </section>

              <section className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
                <PanelTitle title="Source submissions" />
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[820px] border-collapse text-left text-sm">
                    <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                      <tr>
                        <th className="px-5 py-4 font-semibold">Submitted</th>
                        <th className="px-5 py-4 font-semibold">Campaign</th>
                        <th className="px-5 py-4 font-semibold">Sync</th>
                        <th className="px-5 py-4 font-semibold">Preview</th>
                        <th className="px-5 py-4 font-semibold">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {!sortedResponses.length && (
                        <tr>
                          <td colSpan={5} className="px-5 py-8 text-espresso/55">
                            No linked submissions yet.
                          </td>
                        </tr>
                      )}
                      {sortedResponses.map((item) => (
                        <tr key={item.id} className="border-t border-champagne/20 align-top">
                          <td className="px-5 py-4 text-espresso/75">{formatDate(item.submitted_at)}</td>
                          <td className="px-5 py-4 text-espresso/75">{item.form_title}</td>
                          <td className="px-5 py-4 text-espresso/75">{item.contact_sync_status}</td>
                          <td className="max-w-72 px-5 py-4 text-espresso/75">
                            <span className="line-clamp-2 whitespace-pre-wrap">{sourcePreview(item.response_data)}</span>
                          </td>
                          <td className="px-5 py-4">
                            <Link href={`/admin/campaigns/${item.form}/responses`} className="admin-icon-link">
                              <FileText size={15} />
                              Responses
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              <section className="admin-panel">
                <PanelTitle title="Audit trail" />
                <div className="mt-5 grid gap-3">
                  {!contact.audit_events.length && <p className="text-sm text-espresso/55">No audit events yet.</p>}
                  {contact.audit_events.map((event) => (
                    <div key={event.id} className="border border-champagne/20 bg-white/50 p-4 text-sm">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <p className="font-semibold text-espresso">{auditTitle(event.event_type, event.field_name)}</p>
                        <span className="text-xs text-espresso/50">{formatDate(event.created_at)}</span>
                      </div>
                      {event.message && <p className="mt-2 text-espresso/65">{event.message}</p>}
                      {(event.old_value !== null || event.new_value !== null) && (
                        <p className="mt-2 break-words text-espresso/60">
                          {formatUnknown(event.old_value)} → {formatUnknown(event.new_value)}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </div>

            <aside className="grid h-fit gap-6">
              <section className="admin-panel">
                <PanelTitle title="Notes" />
                <textarea value={noteBody} onChange={(event) => setNoteBody(event.target.value)} className="admin-input mt-4 min-h-28" placeholder="Add a private CMS note" />
                <button type="button" onClick={addNote} className="admin-button mt-3">
                  Save note
                </button>
                <div className="mt-5 grid gap-3">
                  {!contact.notes.length && <p className="text-sm text-espresso/55">No notes yet.</p>}
                  {contact.notes.map((note) => (
                    <div key={note.id} className="border border-champagne/20 bg-white/50 p-4 text-sm">
                      <p className="whitespace-pre-wrap text-espresso/75">{note.body}</p>
                      <p className="mt-3 text-xs text-espresso/45">{formatDate(note.created_at)}</p>
                    </div>
                  ))}
                </div>
              </section>

              <section className="admin-panel">
                <PanelTitle title="Possible duplicates" />
                <div className="mt-4 grid gap-3">
                  {!contact.possible_duplicates.length && <p className="text-sm text-espresso/55">No possible duplicates found.</p>}
                  {contact.possible_duplicates.map((duplicate) => (
                    <div key={duplicate.id} className="border border-champagne/20 bg-white/50 p-4 text-sm">
                      <Link href={`/admin/contacts/${duplicate.id}`} className="font-semibold text-espresso underline underline-offset-4">
                        {duplicate.display_name}
                      </Link>
                      <p className="mt-1 text-espresso/60">{duplicate.email || duplicate.phone || "-"}</p>
                      <button type="button" onClick={() => mergeDuplicate(duplicate.id)} className="admin-icon-link mt-3">
                        <Merge size={15} />
                        Merge into this
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            </aside>
          </div>
        )}
      </div>
    </AdminShell>
  );
}

function toDraft(contact: Contact): DraftContact {
  return {
    full_name: contact.full_name,
    email: contact.email,
    phone: contact.phone,
    address: contact.address,
    age: contact.age,
    skin_type: contact.skin_type,
    preferred_ritual: contact.preferred_ritual,
    preferred_day: contact.preferred_day,
    skin_goal: contact.skin_goal,
    marketing_consent: contact.marketing_consent,
    status: contact.status
  };
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

function PanelTitle({ title }: { title: string }) {
  return <h3 className="font-display text-2xl text-espresso">{title}</h3>;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "-";
}

function sourcePreview(data: Record<string, unknown>) {
  const preferred = ["full_name", "name", "email", "phone", "preferred_ritual", "skin_goal"];
  const parts = preferred
    .map((key) => data[key])
    .filter((value) => value !== undefined && value !== null && value !== "")
    .map(formatUnknown);
  return parts.length ? parts.join(" · ") : formatUnknown(data);
}

function auditTitle(eventType: string, fieldName: string) {
  return `${humanize(eventType)}${fieldName ? ` · ${humanize(fieldName)}` : ""}`;
}

function humanize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatUnknown(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
