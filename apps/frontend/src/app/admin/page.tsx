"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Bell, CalendarDays, FileText, Images, Inbox, Palette, RefreshCcw, Sparkles, Users, View } from "lucide-react";
import { CampaignActions } from "@/components/admin/CampaignActions";
import { AdminShell } from "@/components/admin/AdminShell";
import { PublicLink, useAdminList } from "@/components/admin/AdminLists";
import { getFounderDashboard } from "@/lib/api";
import type { FounderDashboardMetric, FounderDashboardResponse } from "@/types/cms";

type Campaign = { id: number; title: string; slug: string; status: string; response_count: number; is_active_now: boolean };
type Page = { id: number; title: string; slug: string; status: string; updated_at: string };
type Ritual = { id: number; title: string; active: boolean; duration: string };
type Contact = { id: number; display_name: string };
type Appointment = { id: number; starts_at: string; status: string };
type ResponseItem = {
  id: number;
  form: number;
  form_title: string;
  form_slug: string;
  submitted_at: string;
  response_data: Record<string, unknown>;
};

export default function AdminDashboardPage() {
  const [period, setPeriod] = useState("today");
  const [founderDashboard, setFounderDashboard] = useState<FounderDashboardResponse | null>(null);
  const [founderLoading, setFounderLoading] = useState(true);
  const [founderError, setFounderError] = useState("");
  const campaigns = useAdminList<Campaign>("/admin/campaign-forms/");
  const pages = useAdminList<Page>("/admin/pages/");
  const rituals = useAdminList<Ritual>("/admin/services/");
  const contacts = useAdminList<Contact>("/admin/contacts/");
  const responses = useAdminList<ResponseItem>("/admin/campaign-responses/");
  const appointments = useAdminList<Appointment>("/admin/appointments/");

  const recentResponses = [...responses.items]
    .sort((left, right) => new Date(right.submitted_at).getTime() - new Date(left.submitted_at).getTime())
    .slice(0, 5);
  const activeCampaigns = campaigns.items.filter((campaign) => campaign.is_active_now).length;
  const totalResponses = campaigns.items.reduce((total, campaign) => total + (campaign.response_count || 0), 0);
  const publishedPages = pages.items.filter((page) => page.status === "published").length;
  const activeRituals = rituals.items.filter((ritual) => ritual.active).length;
  const headlineMetrics = useMemo(() => {
    const metrics = normalizeMetrics(founderDashboard?.headline_metrics || founderDashboard?.metrics);
    return metrics.length
      ? metrics
      : [
          { key: "responses", label: "Total responses", value: totalResponses },
          { key: "contacts", label: "Contacts", value: contacts.items.length },
          { key: "appointments", label: "Appointments", value: appointments.items.length },
          { key: "active_campaigns", label: "Active campaigns", value: activeCampaigns },
          { key: "campaigns", label: "Campaigns", value: campaigns.items.length },
          { key: "published_pages", label: "Published pages", value: publishedPages },
          { key: "active_rituals", label: "Active rituals", value: activeRituals }
        ];
  }, [activeCampaigns, activeRituals, appointments.items.length, campaigns.items.length, contacts.items.length, founderDashboard, publishedPages, totalResponses]);

  async function loadFounderDashboard(nextPeriod = period) {
    setFounderLoading(true);
    setFounderError("");
    try {
      setFounderDashboard(await getFounderDashboard(nextPeriod));
    } catch (err: unknown) {
      setFounderDashboard(null);
      setFounderError(err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Founder metrics are unavailable.");
    } finally {
      setFounderLoading(false);
    }
  }

  useEffect(() => {
    loadFounderDashboard(period);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period]);

  return (
    <AdminShell title="Overview">
      <div className="grid gap-7">
        <section className="overflow-hidden border border-champagne/25 bg-espresso text-ivory shadow-[0_26px_80px_rgba(37,29,24,0.18)]">
          <div className="grid gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:p-7">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-champagne">Command center</p>
              <h2 className="mt-3 font-display text-4xl leading-tight">Founder dashboard for leads, bookings, and studio momentum.</h2>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-ivory/70">
                Headline metrics come from the v1 founder dashboard API, with content and campaign shortcuts kept close for daily admin work.
              </p>
              {founderError && <p className="mt-4 text-sm font-semibold text-red-100">{founderError}</p>}
            </div>
            <div className="flex flex-wrap items-start gap-3 lg:justify-end">
              <label className="min-w-40">
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-ivory/55">Period</span>
                <select value={period} onChange={(event) => setPeriod(event.target.value)} className="admin-input mt-2 border-ivory/20 bg-white/10 text-ivory">
                  <option className="text-espresso" value="today">Today</option>
                  <option className="text-espresso" value="this_week">This week</option>
                  <option className="text-espresso" value="this_month">This month</option>
                  <option className="text-espresso" value="previous_month">Previous month</option>
                  <option className="text-espresso" value="same_period_last_year">Same period last year</option>
                </select>
              </label>
              <button type="button" onClick={() => loadFounderDashboard()} className="admin-button-secondary border-ivory/25 bg-white/8 text-ivory hover:bg-white/14 hover:text-white">
                <RefreshCcw size={16} />
                {founderLoading ? "Refreshing" : "Refresh"}
              </button>
              <Link href="/admin/campaign-responses" className="admin-button bg-champagne text-espresso hover:bg-ivory">
                <Inbox size={16} />
                View responses
              </Link>
              <Link href="/admin/notification-campaigns" className="admin-button-secondary border-ivory/25 bg-white/8 text-ivory hover:bg-white/14 hover:text-white">
                <Bell size={16} />
                Notifications
              </Link>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {headlineMetrics.map((metric) => (
            <Metric key={metric.key} metric={metric} href={hrefForMetric(metric.key)} />
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.8fr)]">
          <div className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
            <PanelHeader title="Campaign performance" actionHref="/admin/campaigns" actionLabel="All campaigns" />
            <div className="overflow-x-auto">
              <table className="w-full min-w-[880px] border-collapse text-left text-sm">
                <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Campaign</th>
                    <th className="px-5 py-4 font-semibold">Status</th>
                    <th className="px-5 py-4 font-semibold">Active</th>
                    <th className="px-5 py-4 font-semibold">Responses</th>
                    <th className="px-5 py-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {campaigns.loading && <TableMessage colSpan={5} message="Loading campaigns..." />}
                  {!campaigns.loading && !campaigns.items.length && <TableMessage colSpan={5} message="No campaigns found." />}
                  {!campaigns.loading &&
                    campaigns.items.map((campaign) => (
                      <tr key={campaign.id} className="border-t border-champagne/20 align-top">
                        <td className="px-5 py-4">
                          <Link href={`/admin/campaigns/${campaign.id}/builder`} className="font-semibold text-espresso underline underline-offset-4">
                            {campaign.title}
                          </Link>
                        </td>
                        <td className="px-5 py-4">
                          <StatusPill value={campaign.status} />
                        </td>
                        <td className="px-5 py-4 text-espresso/72">{campaign.is_active_now ? "Yes" : "No"}</td>
                        <td className="px-5 py-4">
                          <Link href={`/admin/campaigns/${campaign.id}/responses`} className="font-semibold text-espresso underline underline-offset-4">
                            {campaign.response_count || 0}
                          </Link>
                        </td>
                        <td className="px-5 py-3">
                          <CampaignActions campaign={campaign} compact />
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid gap-6">
            <div className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
              <PanelHeader title="Recent responses" actionHref="/admin/campaign-responses" actionLabel="View inbox" />
              <div className="divide-y divide-champagne/20">
                {responses.loading && <p className="p-5 text-sm text-espresso/60">Loading responses...</p>}
                {!responses.loading && !recentResponses.length && <p className="p-5 text-sm text-espresso/60">No responses yet.</p>}
                {!responses.loading &&
                  recentResponses.map((item) => (
                    <Link key={item.id} href={`/admin/campaigns/${item.form}/responses`} className="grid gap-2 p-5 transition hover:bg-white/45">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="font-semibold text-espresso">{valueFor(item, ["full_name", "name"])}</p>
                          <p className="mt-1 text-xs uppercase tracking-[0.12em] text-espresso/50">{item.form_title}</p>
                        </div>
                        <span className="text-xs text-espresso/50">{new Date(item.submitted_at).toLocaleDateString()}</span>
                      </div>
                      <div className="grid gap-1 text-sm text-espresso/65">
                        <span>{valueFor(item, ["email"])}</span>
                        <span>{valueFor(item, ["phone"])}</span>
                      </div>
                    </Link>
                  ))}
              </div>
            </div>

            <div className="border border-champagne/25 bg-ivory/90 p-5 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
              <h3 className="font-display text-2xl text-espresso">Quick actions</h3>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <QuickAction href="/admin/theme" icon={<Palette size={16} />} label="Theme" />
                <QuickAction href="/admin/pages" icon={<FileText size={16} />} label="Pages" />
                <QuickAction href="/admin/hero" icon={<View size={16} />} label="Hero" />
                <QuickAction href="/admin/glow-rituals" icon={<Sparkles size={16} />} label="Rituals" />
                <QuickAction href="/admin/appointments" icon={<CalendarDays size={16} />} label="Appointments" />
                <QuickAction href="/admin/contacts" icon={<Users size={16} />} label="Contacts" />
                <QuickAction href="/admin/notification-campaigns" icon={<Bell size={16} />} label="Notifications" />
                <QuickAction href="/admin/media" icon={<Images size={16} />} label="Media" />
                <QuickAction href="/admin/campaign-responses" icon={<Inbox size={16} />} label="Responses" />
              </div>
              <div className="mt-5 border-t border-champagne/20 pt-4">
                <PublicLink href="/" />
              </div>
            </div>
          </div>
        </section>
      </div>
    </AdminShell>
  );
}

function Metric({ metric, href }: { metric: FounderDashboardMetric; href: string }) {
  return (
    <Link href={href} className="group border border-champagne/25 bg-ivory/90 p-5 shadow-[0_18px_60px_rgba(37,29,24,0.06)] transition hover:-translate-y-0.5 hover:bg-white">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-champagne">{metric.label}</p>
        <ArrowRight size={16} className="text-espresso/35 transition group-hover:translate-x-0.5 group-hover:text-espresso" />
      </div>
      <p className="mt-4 font-display text-5xl leading-none text-espresso">{formatMetricValue(metric.value)}</p>
      {metric.change !== undefined && metric.change !== null && <p className="mt-3 text-sm font-semibold text-espresso/58">{formatMetricValue(metric.change)} vs previous</p>}
      {metric.description && <p className="mt-2 text-sm leading-5 text-espresso/55">{metric.description}</p>}
    </Link>
  );
}

function PanelHeader({ title, actionHref, actionLabel }: { title: string; actionHref: string; actionLabel: string }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-champagne/20 px-5 py-4">
      <h3 className="font-display text-2xl text-espresso">{title}</h3>
      <Link href={actionHref} className="admin-icon-link">
        {actionLabel}
        <ArrowRight size={15} />
      </Link>
    </div>
  );
}

function StatusPill({ value }: { value: string }) {
  const published = value === "published";
  return (
    <span className={`inline-flex px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em] ${published ? "bg-sage/15 text-sage" : "bg-champagne/15 text-espresso/65"}`}>
      {value}
    </span>
  );
}

function QuickAction({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link href={href} className="flex items-center justify-between gap-3 border border-champagne/25 bg-white/55 px-4 py-3 text-sm font-semibold text-espresso transition hover:border-champagne hover:bg-white">
      <span className="flex items-center gap-2">
        {icon}
        {label}
      </span>
      <ArrowRight size={14} className="text-espresso/40" />
    </Link>
  );
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
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function normalizeMetrics(metrics: FounderDashboardResponse["headline_metrics"] | FounderDashboardResponse["metrics"]): FounderDashboardMetric[] {
  if (!metrics) return [];
  if (Array.isArray(metrics)) {
    return metrics.map((metric, index) => ({
      key: metric.key || `metric_${index}`,
      label: metric.label || humanize(String(metric.key || `metric_${index}`)),
      value: metric.value ?? "-"
    }));
  }
  return Object.entries(metrics).map(([key, value]) => {
    if (value && typeof value === "object" && !Array.isArray(value)) {
      const metric = value as FounderDashboardMetric;
      return {
        key: metric.key || key,
        label: metric.label || humanize(key),
        value: metric.value ?? "-",
        change: metric.change,
        description: metric.description
      };
    }
    return { key, label: humanize(key), value: value as string | number };
  });
}

function hrefForMetric(key: string) {
  if (key.includes("appointment") || key.includes("booking")) return "/admin/appointments";
  if (key.includes("contact") || key.includes("customer")) return "/admin/contacts";
  if (key.includes("notification")) return "/admin/notification-campaigns";
  if (key.includes("response") || key.includes("lead")) return "/admin/campaign-responses";
  if (key.includes("campaign")) return "/admin/campaigns";
  if (key.includes("page")) return "/admin/pages";
  if (key.includes("ritual") || key.includes("service")) return "/admin/glow-rituals";
  return "/admin";
}

function formatMetricValue(value: string | number) {
  return typeof value === "number" ? value.toLocaleString("en-IN") : value;
}

function humanize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
