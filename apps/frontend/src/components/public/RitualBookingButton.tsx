"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowRight, CalendarDays, CheckCircle2, Clock, X } from "lucide-react";
import { ApiError, formatApiError, getServiceAvailableSlots, submitRitualBookingLead, submitServiceAppointment } from "@/lib/api";
import { phoneInputValue, validateTypedField } from "@/lib/formValidation";
import type { AvailableSlot, PublicAppFeatureFlags, Service } from "@/types/cms";

type RitualBookingService = Pick<
  Service,
  "title" | "slug" | "cta_url" | "calendly_event_url" | "accepts_online_booking" | "calendly_fallback_enabled"
>;

type BookingDraft = {
  full_name: string;
  phone: string;
  email: string;
  skin_goal: string;
};

const emptyDraft: BookingDraft = {
  full_name: "",
  phone: "",
  email: "",
  skin_goal: ""
};

const calendlyFallbackEmail = "info@theglowmission.com";

export function RitualBookingButton({
  service,
  className,
  bookingFlags,
  children
}: {
  service: RitualBookingService;
  className: string;
  bookingFlags?: PublicAppFeatureFlags;
  children?: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<BookingDraft>(emptyDraft);
  const [date, setDate] = useState(todayIsoDate());
  const [slots, setSlots] = useState<AvailableSlot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<AvailableSlot | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [slotError, setSlotError] = useState("");
  const [scheduled, setScheduled] = useState(false);
  const [confirmedSlot, setConfirmedSlot] = useState<AvailableSlot | null>(null);

  const firstPartyEnabled = Boolean(bookingFlags?.first_party_scheduling) && service.accepts_online_booking !== false;
  const calendlyEnabled = bookingFlags?.calendly_booking !== false && service.calendly_fallback_enabled !== false && Boolean(service.calendly_event_url);
  const currentErrors = useMemo(() => validateDraft(draft), [draft]);
  const canSubmit = Object.keys(currentErrors).length === 0 && (!firstPartyEnabled || Boolean(selectedSlot));

  useEffect(() => {
    function onCalendlyMessage(event: MessageEvent) {
      if (event.origin !== "https://calendly.com") return;
      const data = event.data as { event?: string };
      if (data.event === "calendly.event_scheduled") {
        setScheduled(true);
        setOpen(true);
        setMessage("Your slot has been booked. We have saved your details.");
      }
    }
    window.addEventListener("message", onCalendlyMessage);
    return () => window.removeEventListener("message", onCalendlyMessage);
  }, []);

  useEffect(() => {
    if (!open || !firstPartyEnabled || scheduled) return;
    let ignore = false;
    setLoadingSlots(true);
    setSlotError("");
    setSelectedSlot(null);

    getServiceAvailableSlots(service.slug, date)
      .then((items) => {
        if (ignore) return;
        setSlots(items);
        if (!items.length) {
          setSlotError("No slots are available for this date. Please choose another date.");
        }
      })
      .catch((error) => {
        if (ignore) return;
        setSlots([]);
        setSlotError(error instanceof ApiError ? formatApiError(error.data, "Unable to load slots.") : "Unable to load slots.");
      })
      .finally(() => {
        if (!ignore) setLoadingSlots(false);
      });

    return () => {
      ignore = true;
    };
  }, [date, firstPartyEnabled, open, scheduled, service.slug]);

  function updateField(name: keyof BookingDraft, value: string) {
    setDraft((current) => ({ ...current, [name]: value }));
    setFieldErrors((current) => {
      const next = { ...current };
      const error = validateDraft({ ...draft, [name]: value })[name];
      if (error) {
        next[name] = error;
      } else {
        delete next[name];
      }
      return next;
    });
  }

  function startBooking() {
    if (!firstPartyEnabled && !calendlyEnabled) {
      window.location.href = service.cta_url || "/campaigns/glow-consultation";
      return;
    }
    setOpen(true);
    setScheduled(false);
    setConfirmedSlot(null);
    setMessage("");
    setSlotError("");
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const errors = validateDraft(draft);
    if (Object.keys(errors).length) {
      setFieldErrors(errors);
      return;
    }
    if (!firstPartyEnabled) {
      await continueToCalendly();
      return;
    }
    if (!selectedSlot) {
      setSlotError("Choose a slot to confirm this appointment.");
      return;
    }
    setSubmitting(true);
    setMessage("");
    setSlotError("");
    try {
      const result = await submitServiceAppointment(service.slug, {
        full_name: draft.full_name.trim(),
        phone: draft.phone.trim(),
        email: draft.email.trim() || undefined,
        skin_goal: draft.skin_goal.trim() || undefined,
        customer_notes: draft.skin_goal.trim() || undefined,
        starts_at: selectedSlot.starts_at
      });
      setConfirmedSlot({
        starts_at: result.starts_at || selectedSlot.starts_at,
        ends_at: result.ends_at || selectedSlot.ends_at,
        label: selectedSlot.label
      });
      setScheduled(true);
      setMessage(result.message || "Your appointment is confirmed. We will send the details to your phone.");
    } catch (error) {
      if (error instanceof ApiError) {
        setMessage(formatApiError(error.data, "Unable to confirm this appointment."));
      } else {
        setMessage(error instanceof Error ? error.message : "Unable to confirm this appointment.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  async function continueToCalendly() {
    if (!calendlyEnabled) {
      window.location.href = service.cta_url || "/campaigns/glow-consultation";
      return;
    }
    setSubmitting(true);
    setMessage("");
    try {
      const result = await submitRitualBookingLead(service.slug, draft);
      setMessage(result.message);
      await openCalendly(buildCalendlyUrl(service.calendly_event_url, draft));
      setOpen(false);
    } catch (error) {
      if (error instanceof ApiError) {
        setMessage(formatApiError(error.data, "Unable to save your details."));
      } else {
        setMessage(error instanceof Error ? error.message : "Unable to save your details.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <button type="button" onClick={startBooking} className={className}>
        {children || (
          <>
            Book this ritual
            <ArrowRight size={15} />
          </>
        )}
      </button>

      {open && (
        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-espresso/70 px-4 py-8 backdrop-blur-sm">
          <div className="max-h-[92vh] w-full max-w-3xl overflow-y-auto bg-ivory p-6 text-espresso shadow-[0_34px_100px_rgba(0,0,0,0.28)] md:p-8">
            <div className="flex items-start justify-between gap-4 border-b border-champagne/25 pb-5">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.22em] text-champagne">{scheduled ? "Booking confirmed" : "Book ritual"}</p>
                <h2 className="mt-2 font-display text-3xl leading-tight md:text-4xl">{scheduled ? "Your glow time is saved" : service.title}</h2>
              </div>
              <button type="button" onClick={() => setOpen(false)} className="text-espresso/55 transition hover:text-espresso" aria-label="Close booking modal">
                <X size={22} />
              </button>
            </div>

            {scheduled ? (
              <div className="mt-6 grid gap-5">
                <div className="border border-sage/25 bg-sage/10 p-5">
                  <CheckCircle2 size={26} className="text-sage" />
                  <p className="mt-4 text-sm leading-7 text-espresso/72">{message}</p>
                  {confirmedSlot && (
                    <p className="mt-3 text-sm font-semibold text-espresso">
                      {formatDateTime(confirmedSlot.starts_at)} - {formatTime(confirmedSlot.ends_at)}
                    </p>
                  )}
                </div>
                <button type="button" onClick={() => setOpen(false)} className="brand-button w-fit bg-champagne px-7 py-4 text-sm font-bold text-espresso transition hover:bg-espresso hover:text-ivory">
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={submit} className="mt-6 grid gap-6" noValidate>
                <div className="grid gap-5 md:grid-cols-2">
                  <TextField label="Full name" value={draft.full_name} error={fieldErrors.full_name} onChange={(value) => updateField("full_name", value)} required />
                  <TextField
                    label="Phone"
                    value={draft.phone}
                    error={fieldErrors.phone}
                    inputMode="numeric"
                    onChange={(value) => updateField("phone", phoneInputValue(value).value)}
                    required
                  />
                  <TextField label="Email" value={draft.email} error={fieldErrors.email} inputMode="email" onChange={(value) => updateField("email", value)} />
                  <label>
                    <span className="text-xs font-bold uppercase tracking-[0.16em] text-espresso/58">Skin goal</span>
                    <textarea
                      value={draft.skin_goal}
                      onChange={(event) => updateField("skin_goal", event.target.value)}
                      className="mt-2 min-h-28 w-full border border-champagne/35 bg-white px-4 py-3 text-sm text-espresso outline-none transition focus:border-champagne focus:ring-4 focus:ring-champagne/15"
                    />
                  </label>
                </div>

                {firstPartyEnabled && (
                  <section className="border border-champagne/25 bg-cream/60 p-5">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div>
                        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.18em] text-champagne">
                          <CalendarDays size={15} />
                          Choose date
                        </p>
                        <p className="mt-2 text-sm leading-6 text-espresso/62">Available slots load directly from The Glow Mission calendar.</p>
                      </div>
                      <input
                        type="date"
                        min={todayIsoDate()}
                        value={date}
                        onChange={(event) => setDate(event.target.value)}
                        className="border border-champagne/35 bg-white px-4 py-3 text-sm font-semibold text-espresso outline-none focus:border-champagne focus:ring-4 focus:ring-champagne/15"
                      />
                    </div>

                    <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                      {loadingSlots && <p className="text-sm text-espresso/62">Loading slots...</p>}
                      {!loadingSlots &&
                        slots.map((slot) => {
                          const active = selectedSlot?.starts_at === slot.starts_at;
                          return (
                            <button
                              key={slot.starts_at}
                              type="button"
                              onClick={() => {
                                setSelectedSlot(slot);
                                setSlotError("");
                              }}
                              className={`flex items-center justify-center gap-2 border px-4 py-3 text-sm font-bold transition ${
                                active ? "border-espresso bg-espresso text-ivory" : "border-champagne/35 bg-white/75 text-espresso hover:border-champagne hover:bg-white"
                              }`}
                            >
                              <Clock size={15} />
                              {slot.label || `${formatTime(slot.starts_at)} - ${formatTime(slot.ends_at)}`}
                            </button>
                          );
                        })}
                    </div>

                    {slotError && <div className="mt-4 border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{slotError}</div>}
                    {slotError && calendlyEnabled && (
                      <button type="button" onClick={continueToCalendly} disabled={submitting} className="brand-button mt-4 bg-white px-5 py-3 text-xs font-bold text-espresso ring-1 ring-champagne/35 transition hover:bg-champagne disabled:opacity-55">
                        Use Calendly fallback
                      </button>
                    )}
                  </section>
                )}

                <button type="submit" disabled={submitting || !canSubmit} className="brand-button bg-espresso px-7 py-4 text-sm font-bold text-ivory transition hover:bg-champagne hover:text-espresso disabled:cursor-not-allowed disabled:opacity-55">
                  {submitting ? "Saving..." : firstPartyEnabled ? "Confirm appointment" : "Continue to slots"}
                </button>
                {message && <div className="border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{message}</div>}
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}

function TextField({
  label,
  value,
  error,
  inputMode,
  required,
  onChange
}: {
  label: string;
  value: string;
  error?: string;
  inputMode?: "email" | "numeric";
  required?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label>
      <span className="text-xs font-bold uppercase tracking-[0.16em] text-espresso/58">
        {label}
        {required ? " *" : ""}
      </span>
      <input value={value} onChange={(event) => onChange(event.target.value)} inputMode={inputMode} className="mt-2 w-full border border-champagne/35 bg-white px-4 py-3 text-sm text-espresso outline-none transition focus:border-champagne focus:ring-4 focus:ring-champagne/15" />
      {error && <span className="mt-2 block text-sm font-semibold text-red-700">{error}</span>}
    </label>
  );
}

function validateDraft(draft: BookingDraft): Record<string, string> {
  return Object.fromEntries(
    [
      ["full_name", validateTypedField({ name: "full_name", label: "Full name", fieldType: "text", required: true }, draft.full_name)],
      ["phone", validateTypedField({ name: "phone", label: "Phone", fieldType: "phone", required: true }, draft.phone)],
      ["email", validateTypedField({ name: "email", label: "Email", fieldType: "email", required: false }, draft.email)]
    ].filter(([, error]) => Boolean(error))
  );
}

function buildCalendlyUrl(baseUrl: string, draft: BookingDraft) {
  const url = new URL(baseUrl);
  url.searchParams.set("name", draft.full_name.trim());
  url.searchParams.set("email", draft.email.trim() || calendlyFallbackEmail);
  return url.toString();
}

async function openCalendly(url: string) {
  await Promise.all([loadCalendlyCss(), loadCalendlyScript()]);
  window.Calendly?.initPopupWidget({ url });
}

function loadCalendlyCss() {
  if (document.querySelector('link[data-calendly-widget="true"]')) return Promise.resolve();
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "https://assets.calendly.com/assets/external/widget.css";
  link.dataset.calendlyWidget = "true";
  document.head.appendChild(link);
  return Promise.resolve();
}

function loadCalendlyScript() {
  if (window.Calendly) return Promise.resolve();
  const existing = document.querySelector<HTMLScriptElement>('script[data-calendly-widget="true"]');
  if (existing) {
    return new Promise<void>((resolve) => existing.addEventListener("load", () => resolve(), { once: true }));
  }
  return new Promise<void>((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://assets.calendly.com/assets/external/widget.js";
    script.async = true;
    script.dataset.calendlyWidget = "true";
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Unable to load Calendly."));
    document.body.appendChild(script);
  });
}

function todayIsoDate() {
  const date = new Date();
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 10);
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

declare global {
  interface Window {
    Calendly?: {
      initPopupWidget: (options: { url: string }) => void;
    };
  }
}
