"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowRight, X } from "lucide-react";
import { ApiError, formatApiError, submitRitualBookingLead } from "@/lib/api";
import { phoneInputValue, validateTypedField } from "@/lib/formValidation";

type RitualBookingService = {
  title: string;
  slug: string;
  cta_url: string;
  calendly_event_url: string;
};

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
  children
}: {
  service: RitualBookingService;
  className: string;
  children?: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<BookingDraft>(emptyDraft);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [scheduled, setScheduled] = useState(false);

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

  const currentErrors = useMemo(() => validateDraft(draft), [draft]);
  const canSubmit = Object.keys(currentErrors).length === 0;

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
    if (!service.calendly_event_url) {
      window.location.href = service.cta_url || "/campaigns/glow-consultation";
      return;
    }
    setOpen(true);
    setScheduled(false);
    setMessage("");
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const errors = validateDraft(draft);
    if (Object.keys(errors).length) {
      setFieldErrors(errors);
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
          <div className="max-h-[92vh] w-full max-w-xl overflow-y-auto bg-ivory p-6 text-espresso shadow-[0_34px_100px_rgba(0,0,0,0.28)] md:p-8">
            <div className="flex items-start justify-between gap-4 border-b border-champagne/25 pb-5">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.22em] text-champagne">Book ritual</p>
                <h2 className="mt-2 font-display text-3xl leading-tight">{scheduled ? "Booking confirmed" : service.title}</h2>
              </div>
              <button type="button" onClick={() => setOpen(false)} className="text-espresso/55 transition hover:text-espresso">
                <X size={22} />
              </button>
            </div>

            {scheduled ? (
              <p className="mt-6 text-sm leading-7 text-espresso/70">{message}</p>
            ) : (
              <form onSubmit={submit} className="mt-6 grid gap-5" noValidate>
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
                  <textarea value={draft.skin_goal} onChange={(event) => updateField("skin_goal", event.target.value)} className="mt-2 min-h-28 w-full border border-champagne/35 bg-white px-4 py-3 text-sm text-espresso outline-none transition focus:border-champagne focus:ring-4 focus:ring-champagne/15" />
                </label>
                <button type="submit" disabled={submitting || !canSubmit} className="brand-button bg-espresso px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-ivory transition hover:bg-champagne hover:text-espresso disabled:cursor-not-allowed disabled:opacity-55">
                  {submitting ? "Saving..." : "Continue to slots"}
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

declare global {
  interface Window {
    Calendly?: {
      initPopupWidget: (options: { url: string }) => void;
    };
  }
}
