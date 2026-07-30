"use client";

import Link from "next/link";
import { ArrowLeft, CalendarDays } from "lucide-react";
import { AdminResourceManager, type AdminResourceSaveConfirmationContext } from "@/components/admin/AdminResourceManager";
import { AdminShell } from "@/components/admin/AdminShell";
import { adminFetch } from "@/lib/api";
import type { AppointmentAvailabilityImpact, AppointmentAvailabilityWindow, AppointmentBlock } from "@/types/cms";

const weekdays = [
  { label: "Monday", value: 0 },
  { label: "Tuesday", value: 1 },
  { label: "Wednesday", value: 2 },
  { label: "Thursday", value: 3 },
  { label: "Friday", value: 4 },
  { label: "Saturday", value: 5 },
  { label: "Sunday", value: 6 }
];

export default function AdminAppointmentAvailabilityPage() {
  return (
    <AdminShell title="Appointment Availability">
      <div className="grid gap-7">
        <section className="overflow-hidden border border-champagne/25 bg-espresso text-ivory shadow-[0_26px_80px_rgba(37,29,24,0.18)]">
          <div className="grid gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:p-7">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-champagne">Booking calendar</p>
              <h2 className="mt-3 font-display text-4xl leading-tight">Control bookable hours and blocked time.</h2>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-ivory/70">
                Weekly windows create recurring availability. Blocks close specific dates or times for travel, events, and private holds.
              </p>
            </div>
            <Link href="/admin/appointments" className="admin-button-secondary border-ivory/25 bg-white/8 text-ivory hover:bg-white/14 hover:text-white">
              <ArrowLeft size={16} />
              Back to appointments
            </Link>
          </div>
        </section>

        <AdminResourceManager<AppointmentAvailabilityWindow>
          path="/admin/appointment-availability/"
          title="Weekly availability"
          itemLabel="availability window"
          createLabel="New window"
          defaults={{
            weekday: 0,
            starts_at: "13:30",
            ends_at: "19:30",
            active: true
          }}
          columns={[
            { label: "Day", value: (item) => weekdayName(item.weekday) },
            { label: "Time", value: (item) => `${formatTime(item.starts_at)} - ${formatTime(item.ends_at)}` },
            { label: "Active", value: (item) => (item.active ? "Yes" : "No") }
          ]}
          fields={[
            { name: "weekday", label: "Weekday", type: "select", options: weekdays, required: true },
            { name: "starts_at", label: "Start time", placeholder: "13:30", required: true },
            { name: "ends_at", label: "End time", placeholder: "19:30", required: true },
            { name: "label", label: "Label", placeholder: "Morning / Evening" },
            { name: "active", label: "Active", type: "checkbox" }
          ]}
          transformPayload={(payload) => ({
            ...payload,
            weekday: Number(payload.weekday)
          })}
          confirmSave={confirmWeeklyAvailabilitySave}
          confirmDelete={confirmWeeklyAvailabilityDelete}
          extraActions={() => (
            <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-espresso/45">
              <CalendarDays size={13} />
              Weekly
            </span>
          )}
        />

        <AdminResourceManager<AppointmentBlock>
          path="/admin/appointment-blocks/"
          title="Blocked time"
          itemLabel="block"
          createLabel="New block"
          defaults={{
            starts_at: "",
            ends_at: "",
            reason: "",
            active: true
          }}
          columns={[
            { label: "Starts", value: (item) => formatDateTime(item.starts_at) },
            { label: "Ends", value: (item) => formatDateTime(item.ends_at) },
            { label: "Reason", value: (item) => item.reason || "-" },
            { label: "Active", value: (item) => (item.active ? "Yes" : "No") }
          ]}
          fields={[
            { name: "starts_at", label: "Starts at", type: "datetime", required: true },
            { name: "ends_at", label: "Ends at", type: "datetime", required: true },
            { name: "reason", label: "Reason", span: "full" },
            { name: "active", label: "Active", type: "checkbox" }
          ]}
          transformPayload={(payload) => ({
            ...payload,
            service: payload.service ? Number(payload.service) : null,
            starts_at: normalizeDateTime(payload.starts_at),
            ends_at: normalizeDateTime(payload.ends_at)
          })}
        />
      </div>
    </AdminShell>
  );
}

async function confirmWeeklyAvailabilitySave({ editingId, method, payload }: AdminResourceSaveConfirmationContext<AppointmentAvailabilityWindow>) {
  if (method !== "PATCH" || !editingId) return true;
  const impact = await fetchWeeklyAvailabilityImpact(editingId, payload);
  if (!impactAffectedCount(impact)) return true;
  return confirmAvailabilityImpact("Saving this weekly availability window", impact);
}

async function confirmWeeklyAvailabilityDelete(item: AppointmentAvailabilityWindow) {
  const impact = await fetchWeeklyAvailabilityImpact(item.id, { delete: true });
  if (!impactAffectedCount(impact)) return window.confirm("Delete this availability window?");
  return confirmAvailabilityImpact("Deleting this weekly availability window", impact);
}

function fetchWeeklyAvailabilityImpact(id: number, payload: Record<string, unknown>) {
  return adminFetch<AppointmentAvailabilityImpact>(`/admin/appointment-availability/${id}/impact/`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

function confirmAvailabilityImpact(action: string, impact: AppointmentAvailabilityImpact) {
  const count = impactAffectedCount(impact);
  const visibleAppointments = impact.appointments.slice(0, 5);
  const appointmentLines = visibleAppointments.map((appointment) => {
    const service = appointment.service_title ? ` (${appointment.service_title})` : "";
    const status = appointment.status ? ` [${appointment.status}]` : "";
    return `- ${appointment.full_name || "Unnamed appointment"}${service}: ${formatDateTime(appointment.starts_at)} - ${formatDateTime(appointment.ends_at)}${status}`;
  });
  const remainingCount = Math.max(count - visibleAppointments.length, 0);
  if (remainingCount) {
    appointmentLines.push(`- ...and ${remainingCount} more`);
  }

  return window.confirm(
    [
      `${action} will affect ${count} booked ${count === 1 ? "appointment" : "appointments"}.`,
      "",
      ...appointmentLines,
      "",
      "Continue?"
    ].join("\n")
  );
}

function impactAffectedCount(impact: AppointmentAvailabilityImpact) {
  const count = Number(impact.affected_count);
  return Number.isFinite(count) ? count : impact.appointments.length;
}

function weekdayName(value: number) {
  return weekdays.find((weekday) => Number(weekday.value) === Number(value))?.label || String(value);
}

function normalizeDateTime(value: unknown) {
  if (!value) return "";
  const date = new Date(String(value));
  return Number.isNaN(date.getTime()) ? String(value) : date.toISOString();
}

function formatDateTime(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

function formatTime(value: string) {
  const match = value.match(/^(\d{1,2}):(\d{2})(?::\d{2})?$/);
  if (!match) return value || "-";
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) return value;
  return new Intl.DateTimeFormat("en-IN", {
    hour: "numeric",
    minute: "2-digit",
    timeZone: "UTC"
  }).format(new Date(Date.UTC(2000, 0, 1, hours, minutes)));
}
