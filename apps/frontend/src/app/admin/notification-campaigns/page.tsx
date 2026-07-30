"use client";

import { useEffect, useMemo, useState } from "react";
import { Bell, Eye, RefreshCcw, Save, Send, X } from "lucide-react";
import { AdminShell } from "@/components/admin/AdminShell";
import { useAdminToast } from "@/components/admin/AdminToasts";
import {
  ApiError,
  formatApiError,
  getNotificationCampaignLogs,
  getNotificationCampaignRecipients,
  getNotificationCampaigns,
  saveNotificationCampaign,
  sendNotificationCampaign
} from "@/lib/api";
import type { NotificationCampaign, NotificationCampaignRecipient, NotificationMessageLog } from "@/types/cms";

type ApiList<T> = T[] | { results: T[] };
type Draft = {
  id?: number;
  title: string;
  subject: string;
  body: string;
  marketing_consent_only: boolean;
  include_customers: boolean;
  scheduled_at: string;
};

const emptyDraft: Draft = {
  title: "",
  subject: "",
  body: "",
  marketing_consent_only: true,
  include_customers: true,
  scheduled_at: ""
};

export default function AdminNotificationCampaignsPage() {
  const [campaigns, setCampaigns] = useState<NotificationCampaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [draft, setDraft] = useState<Draft | null>(null);
  const [selected, setSelected] = useState<NotificationCampaign | null>(null);
  const [recipients, setRecipients] = useState<NotificationCampaignRecipient[]>([]);
  const [logs, setLogs] = useState<NotificationMessageLog[]>([]);
  const [recLoading, setRecLoading] = useState(false);
  const [logsLoading, setLogsLoading] = useState(false);
  const toast = useAdminToast();

  const totals = useMemo(
    () => ({
      all: campaigns.length,
      draft: campaigns.filter((item) => item.status === "draft").length,
      sent: campaigns.filter((item) => item.status === "sent").length,
      recipients: campaigns.reduce((total, item) => total + (item.recipient_count || 0), 0)
    }),
    [campaigns]
  );

  async function load() {
    setLoading(true);
    setError("");
    try {
      setCampaigns(unwrap(await getNotificationCampaigns()));
    } catch (err: unknown) {
      const message = err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load notification campaigns.";
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

  function startEdit(campaign: NotificationCampaign) {
    setDraft({
      id: campaign.id,
      title: campaign.title || "",
      subject: campaign.subject || "",
      body: campaign.body || "",
      marketing_consent_only: campaign.marketing_consent_only ?? true,
      include_customers: campaign.include_customers ?? true,
      scheduled_at: toLocalInput(campaign.scheduled_at || "")
    });
  }

  async function save() {
    if (!draft || saving) return;
    setSaving(true);
    try {
      await saveNotificationCampaign({
        id: draft.id,
        title: draft.title.trim(),
        subject: draft.subject.trim(),
        body: draft.body.trim(),
        marketing_consent_only: draft.marketing_consent_only,
        include_customers: draft.include_customers,
        scheduled_at: draft.scheduled_at ? new Date(draft.scheduled_at).toISOString() : null
      });
      setDraft(null);
      toast.success("Notification campaign saved.");
      await load();
    } catch (err: unknown) {
      toast.error(err instanceof ApiError ? formatApiError(err.data, "Unable to save notification campaign.") : err instanceof Error ? err.message : "Unable to save notification campaign.");
    } finally {
      setSaving(false);
    }
  }

  async function send(campaign: NotificationCampaign) {
    if (!window.confirm(`Send notification campaign "${campaign.title}" now?`)) return;
    try {
      await sendNotificationCampaign(campaign.id);
      toast.success("Notification campaign send started.");
      await load();
      if (selected?.id === campaign.id) await reviewRecipients(campaign);
    } catch (err: unknown) {
      toast.error(err instanceof ApiError ? formatApiError(err.data, "Unable to send notification campaign.") : err instanceof Error ? err.message : "Unable to send notification campaign.");
    }
  }

  async function reviewRecipients(campaign: NotificationCampaign) {
    setSelected(campaign);
    setRecLoading(true);
    setLogsLoading(true);
    try {
      const [recipientPayload, logPayload] = await Promise.all([
        getNotificationCampaignRecipients(campaign.id),
        getNotificationCampaignLogs(campaign.id)
      ]);
      setRecipients(unwrap(recipientPayload));
      setLogs(logPayload);
    } catch (err: unknown) {
      setRecipients([]);
      setLogs([]);
      toast.error(err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load notification campaign detail.");
    } finally {
      setRecLoading(false);
      setLogsLoading(false);
    }
  }

  return (
    <AdminShell title="Notifications">
      <div className="grid gap-7">
        <section className="overflow-hidden border border-champagne/25 bg-espresso text-ivory shadow-[0_26px_80px_rgba(37,29,24,0.18)]">
          <div className="grid gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:p-7">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-champagne">Notification campaigns</p>
              <h2 className="mt-3 font-display text-4xl leading-tight">Create, send, and review customer notifications.</h2>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-ivory/70">
                This section is separate from public form Campaigns and uses the v1 notification campaign endpoints.
              </p>
            </div>
            <div className="flex flex-wrap items-start gap-3 lg:justify-end">
              <button type="button" onClick={() => setDraft(emptyDraft)} className="admin-button bg-champagne text-espresso hover:bg-ivory">
                <Bell size={16} />
                New notification
              </button>
              <button type="button" onClick={load} className="admin-button-secondary border-ivory/25 bg-white/8 text-ivory hover:bg-white/14 hover:text-white">
                <RefreshCcw size={16} />
                Refresh
              </button>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-4">
          <Metric label="Campaigns" value={totals.all} />
          <Metric label="Drafts" value={totals.draft} />
          <Metric label="Sent" value={totals.sent} />
          <Metric label="Recipients" value={totals.recipients} />
        </section>

        {draft && (
          <section className="admin-panel">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-champagne/20 pb-5">
              <h3 className="font-display text-2xl text-espresso">{draft.id ? "Edit notification" : "Create notification"}</h3>
              <button type="button" onClick={() => setDraft(null)} className="text-espresso/55 hover:text-espresso" aria-label="Close notification form">
                <X size={20} />
              </button>
            </div>
            <div className="mt-6 grid gap-5 md:grid-cols-2">
              <TextField label="Title" value={draft.title} onChange={(value) => setDraft({ ...draft, title: value })} />
              <TextField label="Subject" value={draft.subject} onChange={(value) => setDraft({ ...draft, subject: value })} />
              <label>
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Scheduled at</span>
                <input value={draft.scheduled_at} onChange={(event) => setDraft({ ...draft, scheduled_at: event.target.value })} type="datetime-local" className="admin-input mt-2" />
              </label>
              <div className="grid gap-3 rounded-none border border-champagne/25 bg-cream/45 p-4">
                <label className="flex items-start gap-3 text-sm text-espresso/72">
                  <input
                    checked={draft.marketing_consent_only}
                    onChange={(event) => setDraft({ ...draft, marketing_consent_only: event.target.checked })}
                    type="checkbox"
                    className="mt-1 h-4 w-4 accent-espresso"
                  />
                  Only contacts with marketing consent
                </label>
                <label className="flex items-start gap-3 text-sm text-espresso/72">
                  <input
                    checked={draft.include_customers}
                    onChange={(event) => setDraft({ ...draft, include_customers: event.target.checked })}
                    type="checkbox"
                    className="mt-1 h-4 w-4 accent-espresso"
                  />
                  Include app customer accounts
                </label>
              </div>
              <label className="md:col-span-2">
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Body</span>
                <textarea value={draft.body} onChange={(event) => setDraft({ ...draft, body: event.target.value })} className="admin-input mt-2 min-h-36" />
              </label>
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <button type="button" disabled={saving} onClick={save} className="admin-button disabled:opacity-55">
                <Save size={16} />
                {saving ? "Saving..." : "Save notification"}
              </button>
              <button type="button" onClick={() => setDraft(null)} className="admin-button-secondary">
                Cancel
              </button>
            </div>
          </section>
        )}

        {loading && <div className="admin-panel text-sm text-espresso/65">Loading notification campaigns...</div>}
        {error && <div className="border border-red-200 bg-red-50 p-8 text-sm text-red-700">{error}</div>}

        {!loading && !error && (
          <section className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1080px] border-collapse text-left text-sm">
                <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Campaign</th>
                    <th className="px-5 py-4 font-semibold">Status</th>
                    <th className="px-5 py-4 font-semibold">Recipients</th>
                    <th className="px-5 py-4 font-semibold">Logs</th>
                    <th className="px-5 py-4 font-semibold">Sent at</th>
                    <th className="px-5 py-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {!campaigns.length && (
                    <tr>
                      <td colSpan={6} className="px-5 py-8 text-espresso/55">
                        No notification campaigns found.
                      </td>
                    </tr>
                  )}
                  {campaigns.map((campaign) => (
                    <tr key={campaign.id} className="border-t border-champagne/20 align-top">
                      <td className="px-5 py-4">
                        <p className="font-semibold text-espresso">{campaign.title}</p>
                        <p className="mt-1 text-espresso/58">{campaign.subject || "-"}</p>
                      </td>
                      <td className="px-5 py-4">
                        <StatusPill value={campaign.status} />
                      </td>
                      <td className="px-5 py-4 text-espresso/75">{campaign.recipient_count ?? "-"}</td>
                      <td className="px-5 py-4 text-espresso/75">{campaign.message_log_count ?? "-"}</td>
                      <td className="px-5 py-4 text-espresso/75">{campaign.sent_at ? formatDate(campaign.sent_at) : "-"}</td>
                      <td className="px-5 py-4">
                        <div className="flex flex-wrap items-center gap-2">
                          <button type="button" onClick={() => startEdit(campaign)} className="admin-icon-link">
                            <Save size={15} />
                            Edit
                          </button>
                          <button type="button" onClick={() => reviewRecipients(campaign)} className="admin-icon-link">
                            <Eye size={15} />
                            Recipients
                          </button>
                          <button type="button" onClick={() => send(campaign)} className="admin-icon-link">
                            <Send size={15} />
                            Send
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

        {selected && (
          <section className="admin-panel">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-champagne/20 pb-5">
              <div>
                <h3 className="font-display text-2xl text-espresso">Recipients and logs</h3>
                <p className="mt-1 text-sm text-espresso/58">{selected.title}</p>
              </div>
              <button type="button" onClick={() => setSelected(null)} className="text-espresso/55 hover:text-espresso" aria-label="Close recipients">
                <X size={20} />
              </button>
            </div>
            <div className="mt-5 overflow-x-auto">
              <table className="w-full min-w-[860px] border-collapse text-left text-sm">
                <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Recipient</th>
                    <th className="px-5 py-4 font-semibold">Contact</th>
                    <th className="px-5 py-4 font-semibold">Status</th>
                    <th className="px-5 py-4 font-semibold">Sent at</th>
                    <th className="px-5 py-4 font-semibold">Log</th>
                  </tr>
                </thead>
                <tbody>
                  {recLoading && <TableMessage colSpan={5} message="Loading recipients..." />}
                  {!recLoading && !recipients.length && <TableMessage colSpan={5} message="No recipients found." />}
                  {!recLoading &&
                    recipients.map((recipient) => (
                      <tr key={`${recipient.contact || "contact"}-${recipient.user || "user"}-${recipient.email || recipient.phone || "recipient"}`} className="border-t border-champagne/20 align-top">
                        <td className="px-5 py-4">
                          <p className="font-semibold text-espresso">{recipient.display_name || "-"}</p>
                          <p className="mt-1 text-espresso/58">{recipient.email || recipient.phone || "-"}</p>
                        </td>
                        <td className="px-5 py-4 text-espresso/75">{recipient.contact || "-"}</td>
                        <td className="px-5 py-4 text-espresso/75">Preview</td>
                        <td className="px-5 py-4 text-espresso/75">-</td>
                        <td className="px-5 py-4 text-espresso/70">Will receive email and push where reachable.</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            <div className="mt-8 border-t border-champagne/20 pt-6">
              <h4 className="font-display text-xl text-espresso">Delivery logs</h4>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[860px] border-collapse text-left text-sm">
                  <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                    <tr>
                      <th className="px-5 py-4 font-semibold">Recipient</th>
                      <th className="px-5 py-4 font-semibold">Channel</th>
                      <th className="px-5 py-4 font-semibold">Status</th>
                      <th className="px-5 py-4 font-semibold">Sent at</th>
                      <th className="px-5 py-4 font-semibold">Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logsLoading && <TableMessage colSpan={5} message="Loading delivery logs..." />}
                    {!logsLoading && !logs.length && <TableMessage colSpan={5} message="No delivery logs yet. Logs appear after sending." />}
                    {!logsLoading &&
                      logs.map((log) => (
                        <tr key={log.id} className="border-t border-champagne/20 align-top">
                          <td className="px-5 py-4">
                            <p className="font-semibold text-espresso">{log.recipient_display_name || "-"}</p>
                            <p className="mt-1 text-espresso/58">{log.recipient_address || "-"}</p>
                          </td>
                          <td className="px-5 py-4 text-espresso/75">{humanize(log.channel)}</td>
                          <td className="px-5 py-4">
                            <StatusPill value={log.status} />
                          </td>
                          <td className="px-5 py-4 text-espresso/75">{log.sent_at ? formatDate(log.sent_at) : "-"}</td>
                          <td className="px-5 py-4 text-espresso/70">{log.error || "-"}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )}
      </div>
    </AdminShell>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-champagne/25 bg-ivory/90 p-5 shadow-[0_18px_60px_rgba(37,29,24,0.06)]">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-champagne">{label}</p>
      <p className="mt-3 font-display text-4xl leading-none text-espresso">{value.toLocaleString("en-IN")}</p>
    </div>
  );
}

function TextField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label>
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">{label}</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} className="admin-input mt-2" />
    </label>
  );
}

function StatusPill({ value }: { value: string }) {
  const tone = value === "sent" ? "bg-sage/15 text-sage" : value === "draft" ? "bg-champagne/15 text-espresso/70" : value === "cancelled" ? "bg-red-50 text-red-700" : "bg-espresso/10 text-espresso";
  return <span className={`inline-flex px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em] ${tone}`}>{humanize(value)}</span>;
}

function TableMessage({ message, colSpan }: { message: string; colSpan: number }) {
  return (
    <tr>
      <td className="px-5 py-8 text-espresso/55" colSpan={colSpan}>
        {message}
      </td>
    </tr>
  );
}

function unwrap<T>(data: ApiList<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" }) : "-";
}

function toLocalInput(value: string) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function humanize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
