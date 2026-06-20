"use client";

import { useMemo, useState } from "react";
import { submitCampaignResponse } from "@/lib/api";
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

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("submitting");
    setMessage("");
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
      setMessage(error instanceof Error ? error.message : "Unable to submit the form.");
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
          />
          {field.help_text && <span className="mt-2 block text-sm text-espresso/55">{field.help_text}</span>}
        </label>
      ))}
      <button
        type="submit"
        disabled={status === "submitting"}
        className="w-full bg-champagne px-7 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-espresso disabled:opacity-60"
      >
        {status === "submitting" ? "Sending..." : "Submit"}
      </button>
      {message && <p className={`text-sm ${status === "success" ? "text-espresso" : "text-red-700"}`}>{message}</p>}
    </form>
  );
}

function FieldInput({
  field,
  value,
  onChange
}: {
  field: CampaignForm["fields"][number];
  value: string | boolean;
  onChange: (value: string | boolean) => void;
}) {
  const baseClass = "mt-3 w-full border border-champagne/35 bg-ivory px-4 py-4 text-base text-espresso outline-none transition focus:border-champagne";
  if (field.field_type === "textarea") {
    return <textarea required={field.required} placeholder={field.placeholder} className={`${baseClass} min-h-36`} value={String(value)} onChange={(event) => onChange(event.target.value)} />;
  }
  if (field.field_type === "select") {
    return (
      <select required={field.required} className={baseClass} value={String(value)} onChange={(event) => onChange(event.target.value)}>
        <option value="">Choose an option</option>
        {field.options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    );
  }
  if (field.field_type === "checkbox") {
    return (
      <span className="mt-3 flex items-center gap-3 text-sm text-espresso/70">
        <input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(event.target.checked)} className="h-5 w-5 accent-champagne" />
        Yes
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

