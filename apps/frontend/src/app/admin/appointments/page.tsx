"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Camera, CalendarDays, CheckCircle2, Clock, Plus, RefreshCcw, Save, Upload, X } from "lucide-react";
import { AdminShell } from "@/components/admin/AdminShell";
import { useAdminToast } from "@/components/admin/AdminToasts";
import { ApiError, adminFetch, createAppointmentPhoto, flattenApiErrors, formatApiError, getAppointmentPhotos } from "@/lib/api";
import { phoneInputValue } from "@/lib/formValidation";
import type { Appointment, AppointmentPhoto, AppointmentStatus, ContactSummary, Service } from "@/types/cms";

type ApiList<T> = T[] | { results: T[] };
type TimeFilter = "today" | "upcoming" | "all";

type AppointmentDraft = {
  service: string;
  contact: string;
  full_name: string;
  phone: string;
  email: string;
  skin_goal: string;
  customer_notes: string;
  starts_at: string;
  status: AppointmentStatus | string;
};

const statusOptions: Array<{ label: string; value: AppointmentStatus | string }> = [
  { label: "Confirmed", value: "confirmed" },
  { label: "Completed", value: "completed" },
  { label: "Cancelled", value: "cancelled" },
  { label: "No show", value: "no_show" }
];

const emptyDraft: AppointmentDraft = {
  service: "",
  contact: "",
  full_name: "",
  phone: "",
  email: "",
  skin_goal: "",
  customer_notes: "",
  starts_at: "",
  status: "confirmed"
};

export default function AdminAppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [contacts, setContacts] = useState<ContactSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [timeFilter, setTimeFilter] = useState<TimeFilter>("today");
  const [statusFilter, setStatusFilter] = useState("");
  const [draft, setDraft] = useState<AppointmentDraft | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [photoAppointment, setPhotoAppointment] = useState<Appointment | null>(null);
  const [photos, setPhotos] = useState<AppointmentPhoto[]>([]);
  const [photoDraft, setPhotoDraft] = useState({ photo_type: "before", notes: "" });
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoLoading, setPhotoLoading] = useState(false);
  const toast = useAdminToast();

  const filteredAppointments = useMemo(() => {
    return appointments
      .filter((appointment) => {
        if (statusFilter && appointment.status !== statusFilter) return false;
        if (timeFilter === "today") return isToday(appointment.starts_at);
        if (timeFilter === "upcoming") return new Date(appointment.starts_at).getTime() >= startOfToday().getTime();
        return true;
      })
      .sort((left, right) => new Date(left.starts_at).getTime() - new Date(right.starts_at).getTime());
  }, [appointments, statusFilter, timeFilter]);

  const todayCount = appointments.filter((appointment) => isToday(appointment.starts_at)).length;
  const upcomingCount = appointments.filter((appointment) => new Date(appointment.starts_at).getTime() >= startOfToday().getTime()).length;
  const cancelledCount = appointments.filter((appointment) => appointment.status === "cancelled").length;

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [appointmentData, serviceData, contactData] = await Promise.all([
        adminFetch<ApiList<Appointment>>("/admin/appointments/"),
        adminFetch<ApiList<Service>>("/admin/services/"),
        adminFetch<ApiList<ContactSummary>>("/admin/contacts/")
      ]);
      setAppointments(unwrap(appointmentData));
      setServices(unwrap(serviceData));
      setContacts(unwrap(contactData));
    } catch (err: unknown) {
      const message = err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load appointments.";
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

  function startCreate() {
    setFieldErrors({});
    setDraft({
      ...emptyDraft,
      starts_at: defaultAppointmentStart()
    });
  }

  function updateDraft(next: Partial<AppointmentDraft>) {
    setDraft((current) => (current ? { ...current, ...next } : current));
  }

  function updateContact(contactId: string) {
    const contact = contacts.find((item) => String(item.id) === contactId);
    updateDraft({
      contact: contactId,
      full_name: contact?.full_name || contact?.display_name || draft?.full_name || "",
      phone: contact?.phone || draft?.phone || "",
      email: contact?.email || draft?.email || ""
    });
  }

  async function createAppointment() {
    if (!draft || saving) return;
    setSaving(true);
    setFieldErrors({});
    try {
      await adminFetch<Appointment>("/admin/appointments/", {
        method: "POST",
        body: JSON.stringify({
          service: draft.service ? Number(draft.service) : null,
          contact: draft.contact ? Number(draft.contact) : null,
          full_name: draft.full_name.trim(),
          phone: draft.phone.trim(),
          email: draft.email.trim(),
          skin_goal: draft.skin_goal.trim(),
          customer_notes: draft.customer_notes.trim(),
          starts_at: localInputToIso(draft.starts_at),
          status: draft.status
        })
      });
      setDraft(null);
      toast.success("Appointment created.");
      await load();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setFieldErrors(flattenApiErrors(err.data));
        toast.error(formatApiError(err.data, "Unable to create appointment."));
      } else {
        toast.error(err instanceof Error ? err.message : "Unable to create appointment.");
      }
    } finally {
      setSaving(false);
    }
  }

  async function updateStatus(appointment: Appointment, status: string) {
    try {
      await adminFetch<Appointment>(`/admin/appointments/${appointment.id}/`, {
        method: "PATCH",
        body: JSON.stringify({ status })
      });
      toast.success("Appointment updated.");
      await load();
    } catch (err: unknown) {
      const message = err instanceof ApiError ? formatApiError(err.data, "Unable to update appointment.") : err instanceof Error ? err.message : "Unable to update appointment.";
      toast.error(message);
    }
  }

  async function openPhotos(appointment: Appointment) {
    setPhotoAppointment(appointment);
    setPhotoLoading(true);
    try {
      setPhotos(await getAppointmentPhotos(appointment.id));
    } catch (err: unknown) {
      setPhotos(appointment.photos || []);
      toast.error(err instanceof Error && err.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load appointment photos.");
    } finally {
      setPhotoLoading(false);
    }
  }

  async function uploadPhoto() {
    if (!photoAppointment || !photoFile) return;
    const form = new FormData();
    form.set("image", photoFile);
    form.set("photo_type", photoDraft.photo_type);
    form.set("notes", photoDraft.notes);
    try {
      await createAppointmentPhoto(photoAppointment.id, form);
      setPhotoFile(null);
      setPhotoDraft({ photo_type: "before", notes: "" });
      toast.success("Photo uploaded.");
      await openPhotos(photoAppointment);
      await load();
    } catch (err: unknown) {
      toast.error(err instanceof ApiError ? formatApiError(err.data, "Unable to upload photo.") : err instanceof Error ? err.message : "Unable to upload photo.");
    }
  }

  return (
    <AdminShell title="Appointments">
      <div className="grid gap-7">
        <section className="overflow-hidden border border-champagne/25 bg-espresso text-ivory shadow-[0_26px_80px_rgba(37,29,24,0.18)]">
          <div className="grid gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:p-7">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-champagne">Daily schedule</p>
              <h2 className="mt-3 font-display text-4xl leading-tight">Appointments, confirmations, and follow-ups.</h2>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-ivory/70">
                Create bookings from calls, review today&apos;s calendar, and keep ritual appointments in one operational view.
              </p>
            </div>
            <div className="flex flex-wrap items-start gap-3 lg:justify-end">
              <button type="button" onClick={startCreate} className="admin-button bg-champagne text-espresso hover:bg-ivory">
                <Plus size={16} />
                New appointment
              </button>
              <Link href="/admin/appointments/availability" className="admin-button-secondary border-ivory/25 bg-white/8 text-ivory hover:bg-white/14 hover:text-white">
                <CalendarDays size={16} />
                Availability
              </Link>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          <Metric label="Today" value={todayCount} icon={<CalendarDays size={18} />} />
          <Metric label="Upcoming" value={upcomingCount} icon={<Clock size={18} />} />
          <Metric label="Cancelled" value={cancelledCount} icon={<CheckCircle2 size={18} />} />
        </section>

        <section className="admin-panel">
          <div className="grid gap-4 lg:grid-cols-[1fr_220px_220px_auto] lg:items-end">
            <div>
              <h3 className="font-display text-2xl text-espresso">Schedule filters</h3>
              <p className="mt-2 text-sm text-espresso/60">{filteredAppointments.length} appointments in this view</p>
            </div>
            <label>
              <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">When</span>
              <select value={timeFilter} onChange={(event) => setTimeFilter(event.target.value as TimeFilter)} className="admin-input mt-2">
                <option value="today">Today</option>
                <option value="upcoming">Upcoming</option>
                <option value="all">All appointments</option>
              </select>
            </label>
            <label>
              <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Status</span>
              <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} className="admin-input mt-2">
                <option value="">All statuses</option>
                {statusOptions.map((status) => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
            </label>
            <button type="button" onClick={load} className="admin-button-secondary">
              <RefreshCcw size={16} />
              Refresh
            </button>
          </div>
        </section>

        {draft && (
          <section className="admin-panel">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-champagne/20 pb-5">
              <h3 className="font-display text-2xl text-espresso">Create appointment</h3>
              <button type="button" onClick={() => setDraft(null)} className="text-espresso/55 hover:text-espresso" aria-label="Close create appointment form">
                <X size={20} />
              </button>
            </div>
            <div className="mt-6 grid gap-5 md:grid-cols-2">
              <label>
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Ritual</span>
                <select value={draft.service} onChange={(event) => updateDraft({ service: event.target.value })} className="admin-input mt-2">
                  <option value="">No ritual selected</option>
                  {services.map((service) => (
                    <option key={service.id} value={service.id}>
                      {service.title}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Linked contact</span>
                <select value={draft.contact} onChange={(event) => updateContact(event.target.value)} className="admin-input mt-2">
                  <option value="">No linked contact</option>
                  {contacts.map((contact) => (
                    <option key={contact.id} value={contact.id}>
                      {contact.display_name}
                    </option>
                  ))}
                </select>
              </label>
              <TextField label="Full name" value={draft.full_name} error={fieldErrors.full_name} onChange={(value) => updateDraft({ full_name: value })} />
              <TextField label="Phone" value={draft.phone} error={fieldErrors.phone} inputMode="numeric" onChange={(value) => updateDraft({ phone: phoneInputValue(value).value })} />
              <TextField label="Email" value={draft.email} error={fieldErrors.email} inputMode="email" onChange={(value) => updateDraft({ email: value })} />
              <label>
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Starts at</span>
                <input value={draft.starts_at} onChange={(event) => updateDraft({ starts_at: event.target.value })} type="datetime-local" className="admin-input mt-2" />
                {fieldErrors.starts_at && <span className="mt-2 block text-sm font-semibold text-red-700">{fieldErrors.starts_at}</span>}
              </label>
              <label>
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Status</span>
                <select value={draft.status} onChange={(event) => updateDraft({ status: event.target.value })} className="admin-input mt-2">
                  {statusOptions.map((status) => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="md:col-span-2">
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Skin goal</span>
                <textarea value={draft.skin_goal} onChange={(event) => updateDraft({ skin_goal: event.target.value })} className="admin-input mt-2 min-h-24" />
              </label>
              <label className="md:col-span-2">
                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Internal notes</span>
                <textarea value={draft.customer_notes} onChange={(event) => updateDraft({ customer_notes: event.target.value })} className="admin-input mt-2 min-h-24" />
              </label>
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <button type="button" disabled={saving} className="admin-button disabled:opacity-55" onClick={createAppointment}>
                <Save size={16} />
                {saving ? "Saving..." : "Create appointment"}
              </button>
              <button type="button" className="admin-button-secondary" onClick={() => setDraft(null)}>
                Cancel
              </button>
            </div>
          </section>
        )}

        {loading && <div className="admin-panel text-sm text-espresso/65">Loading appointments...</div>}
        {error && <div className="border border-red-200 bg-red-50 p-8 text-sm text-red-700">{error}</div>}

        {!loading && !error && (
          <section className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1080px] border-collapse text-left text-sm">
                <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
                  <tr>
                    <th className="px-5 py-4 font-semibold">Time</th>
                    <th className="px-5 py-4 font-semibold">Client</th>
                    <th className="px-5 py-4 font-semibold">Ritual</th>
                    <th className="px-5 py-4 font-semibold">Status</th>
                    <th className="px-5 py-4 font-semibold">Phone</th>
                    <th className="px-5 py-4 font-semibold">Photos</th>
                    <th className="px-5 py-4 font-semibold">Notes</th>
                    <th className="px-5 py-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {!filteredAppointments.length && (
                    <tr>
                      <td colSpan={8} className="px-5 py-8 text-espresso/55">
                        No appointments found.
                      </td>
                    </tr>
                  )}
                  {filteredAppointments.map((appointment) => (
                    <tr key={appointment.id} className="border-t border-champagne/20 align-top">
                      <td className="px-5 py-4">
                        <p className="font-semibold text-espresso">{formatDateTime(appointment.starts_at)}</p>
                        {appointment.ends_at && <p className="mt-1 text-xs text-espresso/50">Until {formatTime(appointment.ends_at)}</p>}
                      </td>
                      <td className="px-5 py-4">
                        <p className="font-semibold text-espresso">{appointment.contact_display_name || appointment.full_name || "-"}</p>
                        {appointment.contact && (
                          <Link href={`/admin/contacts/${appointment.contact}`} className="mt-1 inline-flex text-xs font-semibold uppercase tracking-[0.12em] text-champagne">
                            Open contact
                          </Link>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        {appointment.service_slug ? (
                          <Link href={`/glow-rituals/${appointment.service_slug}`} target="_blank" className="font-semibold text-espresso underline underline-offset-4">
                            {appointment.service_title || "Ritual"}
                          </Link>
                        ) : (
                          <span className="text-espresso/70">{appointment.service_title || "-"}</span>
                        )}
                      </td>
                      <td className="px-5 py-4">
                        <StatusPill value={appointment.status} />
                      </td>
                      <td className="px-5 py-4 text-espresso/75">{appointment.phone || "-"}</td>
                      <td className="px-5 py-4">
                        <button type="button" onClick={() => openPhotos(appointment)} className="admin-icon-link">
                          <Camera size={15} />
                          {appointment.photo_count ?? appointment.photos?.length ?? 0} photos
                        </button>
                      </td>
                      <td className="px-5 py-4 text-espresso/70">{appointment.customer_notes || appointment.skin_goal || "-"}</td>
                      <td className="px-5 py-4">
                        <div className="flex flex-wrap items-center gap-2">
                          {statusOptions.map((status) => (
                            <button
                              key={status.value}
                              type="button"
                              disabled={appointment.status === status.value}
                              onClick={() => updateStatus(appointment, status.value)}
                              className="admin-icon-link disabled:cursor-not-allowed disabled:opacity-35"
                            >
                              {status.label}
                            </button>
                          ))}
                          {appointment.service_slug && (
                            <Link href={`/glow-rituals/${appointment.service_slug}`} target="_blank" className="admin-icon-link">
                              View ritual
                              <ArrowRight size={15} />
                            </Link>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {photoAppointment && (
          <section className="admin-panel">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-champagne/20 pb-5">
              <div>
                <h3 className="font-display text-2xl text-espresso">Appointment photos</h3>
                <p className="mt-1 text-sm text-espresso/58">
                  {photoAppointment.contact_display_name || photoAppointment.full_name || "Appointment"} · {formatDateTime(photoAppointment.starts_at)}
                </p>
              </div>
              <button type="button" onClick={() => setPhotoAppointment(null)} className="text-espresso/55 hover:text-espresso" aria-label="Close appointment photos">
                <X size={20} />
              </button>
            </div>

            <div className="mt-6 grid gap-6 xl:grid-cols-[360px_1fr]">
              <div className="grid gap-4">
                <label>
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Photo</span>
                  <input type="file" accept="image/*" onChange={(event) => setPhotoFile(event.target.files?.[0] || null)} className="admin-input mt-2" />
                </label>
                <label>
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Type</span>
                  <select value={photoDraft.photo_type} onChange={(event) => setPhotoDraft({ ...photoDraft, photo_type: event.target.value })} className="admin-input mt-2">
                    <option value="before">Before</option>
                    <option value="after">After</option>
                  </select>
                </label>
                <label>
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">Notes</span>
                  <textarea value={photoDraft.notes} onChange={(event) => setPhotoDraft({ ...photoDraft, notes: event.target.value })} className="admin-input mt-2 min-h-24" />
                </label>
                <button type="button" onClick={uploadPhoto} disabled={!photoFile} className="admin-button disabled:cursor-not-allowed disabled:opacity-50">
                  <Upload size={16} />
                  Upload photo
                </button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {photoLoading && <p className="text-sm text-espresso/60">Loading photos...</p>}
                {!photoLoading && !photos.length && <p className="text-sm text-espresso/60">No photos attached.</p>}
                {!photoLoading &&
                  photos.map((photo) => (
                    <div key={photo.id} className="border border-champagne/20 bg-white/50 p-3">
                      {photo.image_url && <img src={photo.image_url} alt={`${photo.photo_type || "Appointment"} photo`} className="aspect-[4/3] w-full object-cover" />}
                      <div className="mt-3 grid gap-2">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-espresso/55">{photo.photo_type || "photo"}</span>
                          <span className="text-xs text-espresso/45">#{photo.id}</span>
                        </div>
                        {photo.notes && <p className="text-sm text-espresso/65">{photo.notes}</p>}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </section>
        )}
      </div>
    </AdminShell>
  );
}

function Metric({ label, value, icon }: { label: string; value: number; icon: React.ReactNode }) {
  return (
    <div className="border border-champagne/25 bg-ivory/90 p-5 shadow-[0_18px_60px_rgba(37,29,24,0.06)]">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-champagne">{label}</p>
        <span className="text-espresso/45">{icon}</span>
      </div>
      <p className="mt-4 font-display text-5xl leading-none text-espresso">{value}</p>
    </div>
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

function StatusPill({ value }: { value: string }) {
  const tone = value === "confirmed" ? "bg-sage/15 text-sage" : value === "cancelled" ? "bg-red-50 text-red-700" : value === "completed" ? "bg-espresso/10 text-espresso" : "bg-champagne/15 text-espresso/70";
  return <span className={`inline-flex px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em] ${tone}`}>{humanizeStatus(value)}</span>;
}

function unwrap<T>(data: ApiList<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function startOfToday() {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

function isToday(value: string) {
  const date = new Date(value);
  const today = startOfToday();
  return date.getFullYear() === today.getFullYear() && date.getMonth() === today.getMonth() && date.getDate() === today.getDate();
}

function defaultAppointmentStart() {
  const date = new Date();
  date.setHours(date.getHours() + 1, 0, 0, 0);
  return toLocalInput(date.toISOString());
}

function localInputToIso(value: string) {
  return value ? new Date(value).toISOString() : "";
}

function toLocalInput(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString("en-IN", {
    hour: "numeric",
    minute: "2-digit"
  });
}

function humanizeStatus(value: string) {
  return value.replace(/_/g, " ");
}
