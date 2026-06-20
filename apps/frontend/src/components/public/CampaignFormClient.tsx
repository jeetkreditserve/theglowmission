"use client";

import { useMemo, useState } from "react";
import { ApiError, flattenApiErrors, formatApiError, submitCampaignResponse } from "@/lib/api";
import type { CampaignForm } from "@/types/cms";

export function CampaignFormClient({ form }: { form: CampaignForm }) {
  const initialState = useMemo(
    () =>
      Object.fromEntries(
        form.fields.map((field) => [field.key, field.field_type === "checkbox" ? false : ""])
      ) as Record<string, string | boolean>,
    [form.fields]
  );
  const [values, setValues] = useState<Record<string, string | boolean>>(initialState);
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("submitting");
    setMessage("");
    setFieldErrors({});
    try {
      const result = await submitCampaignResponse(form.slug, values);
      setStatus("success");
      setMessage(result.message || form.success_message);
      setValues(initialState);
      if (result.redirect_url) {
        window.location.href = result.redirect_url;
      }
    } catch (error) {
      setStatus("error");
      if (error instanceof ApiError) {
        const responseErrors = (error.data as { response_data?: unknown } | null)?.response_data;
        setFieldErrors(flattenApiErrors(responseErrors));
        setMessage(formatApiError(responseErrors || error.data, form.error_message || "Please check the highlighted fields and try again."));
        return;
      }
      setMessage(error instanceof Error ? error.message : form.error_message || "Please check the highlighted fields and try again.");
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      {form.fields.map((field) => (
        <label key={field.id} className="block">
          <span className="text-sm font-semibold uppercase tracking-[0.16em] text-espresso/70">
            {field.label}
            {field.required ? " *" : ""}
          </span>
          <FieldInput
            field={field}
            value={values[field.key]}
            onChange={(value) => setValues((current) => ({ ...current, [field.key]: value }))}
            emptySelectLabel={form.empty_select_label}
            checkboxLabel={form.checkbox_label}
          />
          {field.help_text && <span className="mt-2 block text-sm text-espresso/55">{field.help_text}</span>}
          {fieldErrors[field.key] && <span className="mt-2 block text-sm font-semibold text-red-700">{fieldErrors[field.key]}</span>}
        </label>
      ))}
      <button
        type="submit"
        disabled={status === "submitting"}
        className="brand-button w-full bg-espresso px-7 py-4 text-sm font-bold text-ivory transition hover:bg-champagne hover:text-espresso disabled:opacity-60"
      >
        {status === "submitting" ? form.submitting_label || form.button_label : form.button_label}
      </button>
      {message && <div className={`border px-4 py-3 text-sm ${status === "success" ? "border-champagne/30 bg-cream text-espresso" : "border-red-200 bg-red-50 text-red-700"}`}>{message}</div>}
    </form>
  );
}

function FieldInput({
  field,
  value,
  onChange,
  emptySelectLabel,
  checkboxLabel
}: {
  field: CampaignForm["fields"][number];
  value: string | boolean;
  onChange: (value: string | boolean) => void;
  emptySelectLabel: string;
  checkboxLabel: string;
}) {
  const baseClass = "mt-3 w-full border border-champagne/35 bg-white px-4 py-4 text-base text-espresso outline-none transition focus:border-champagne focus:ring-4 focus:ring-champagne/15";
  if (field.field_type === "textarea") {
    return <textarea required={field.required} placeholder={field.placeholder} className={`${baseClass} min-h-36`} value={String(value)} onChange={(event) => onChange(event.target.value)} />;
  }
  if (field.field_type === "select") {
    return (
      <select required={field.required} className={baseClass} value={String(value)} onChange={(event) => onChange(event.target.value)}>
        <option value="">{emptySelectLabel}</option>
        {field.options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  }
  if (field.field_type === "radio") {
    return (
      <span className="mt-3 grid gap-3">
        {field.options.map((option) => (
          <label key={option} className="flex items-center gap-3 border border-champagne/25 bg-white px-4 py-3 text-sm text-espresso/72">
            <input type="radio" required={field.required} name={field.key} checked={value === option} onChange={() => onChange(option)} className="h-4 w-4 accent-champagne" />
            {option}
          </label>
        ))}
      </span>
    );
  }
  if (field.field_type === "checkbox") {
    return (
      <span className="mt-3 flex items-center gap-3 text-sm text-espresso/70">
        <input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(event.target.checked)} className="h-5 w-5 accent-champagne" />
        {checkboxLabel}
      </span>
    );
  }
  return (
    <input
      required={field.required}
      type={field.field_type === "phone" ? "tel" : field.field_type}
      placeholder={field.placeholder}
      className={baseClass}
      value={String(value)}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
