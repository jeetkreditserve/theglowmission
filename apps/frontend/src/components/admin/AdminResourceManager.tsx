"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ExternalLink, Pencil, Plus, RefreshCcw, Save, Trash2, Upload, X } from "lucide-react";
import { useAdminToast } from "@/components/admin/AdminToasts";
import { ApiError, adminFetch, flattenApiErrors, formatApiError } from "@/lib/api";
import { phoneInputValue, stripPhoneDigits, validateTypedFields } from "@/lib/formValidation";

type ApiList<T> = T[] | { results: T[] };

export type FieldType = "text" | "textarea" | "email" | "phone" | "select" | "number" | "checkbox" | "date" | "datetime" | "image" | "json" | "jsonList";

export type FieldConfig<T> = {
  name: keyof T & string;
  label: string;
  type?: FieldType;
  options?: Array<{ label: string; value: string | number | boolean }>;
  placeholder?: string;
  help?: string;
  readOnly?: boolean;
  required?: boolean;
  validation?: Record<string, unknown>;
  span?: "full" | "half";
};

export type ColumnConfig<T> = {
  label: string;
  value: (item: T) => React.ReactNode;
};

function unwrap<T>(data: ApiList<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function fieldValue(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (Array.isArray(value)) return value.join("\n");
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function parseFieldValue(type: FieldType, value: unknown) {
  if (type === "checkbox") return Boolean(value);
  if (type === "number") return value === "" || value === null || value === undefined ? null : Number(value);
  if (type === "phone") return stripPhoneDigits(fieldValue(value));
  if (type === "date") return value === "" || value === null || value === undefined ? null : value;
  if (type === "datetime") return value === "" || value === null || value === undefined ? null : value;
  if (type === "jsonList") {
    if (Array.isArray(value)) return value;
    return String(value || "")
      .split(/\n|,/)
      .map((part) => part.trim())
      .filter(Boolean);
  }
  if (type === "json") {
    if (!value) return {};
    if (typeof value !== "string") return value;
    try {
      return JSON.parse(value);
    } catch {
      throw new Error("Enter valid JSON.");
    }
  }
  return value ?? "";
}

export function AdminResourceManager<T extends { id: number }>({
  path,
  title,
  itemLabel,
  columns,
  fields,
  defaults,
  getPreviewHref,
  getEditHref,
  transformPayload,
  createLabel = "New item",
  queryKey
}: {
  path: string;
  title: string;
  itemLabel: string;
  columns: Array<ColumnConfig<T>>;
  fields: Array<FieldConfig<T>>;
  defaults: Partial<T>;
  getPreviewHref?: (item: T) => string;
  getEditHref?: (item: T) => string;
  transformPayload?: (payload: Record<string, unknown>) => Record<string, unknown>;
  createLabel?: string;
  queryKey?: string;
}) {
  const [items, setItems] = useState<T[]>([]);
  const [draft, setDraft] = useState<Partial<T> | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState("");
  const toast = useAdminToast();

  const listPath = useMemo(() => (queryKey ? `${path}?${queryKey}` : path), [path, queryKey]);

  const load = useCallback(async () => {
    setLoading(true);
    setStatus("");
    setFormError("");
    try {
      const data = await adminFetch<ApiList<T>>(listPath);
      setItems(unwrap(data));
    } catch (error) {
      const message = error instanceof Error && error.message === "AUTH_REQUIRED" ? "Sign in to continue." : "Unable to load data.";
      setStatus(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, [listPath, toast]);

  useEffect(() => {
    load();
  }, [load]);

  function startCreate() {
    setEditingId(null);
    setDraft(defaults);
    setFiles({});
    setFieldErrors({});
    setFormError("");
    setStatus("");
  }

  function startEdit(item: T) {
    setEditingId(item.id);
    setDraft(item);
    setFiles({});
    setFieldErrors({});
    setFormError("");
    setStatus("");
  }

  function cancel() {
    setDraft(null);
    setEditingId(null);
    setFiles({});
    setFieldErrors({});
    setFormError("");
  }

  function updateField(name: string, value: unknown, inlineError = "") {
    setDraft((current) => ({ ...(current || defaults), [name]: value }));
    setFieldErrors((current) => {
      if (!inlineError && !(name in current)) return current;
      const next = { ...current };
      if (inlineError) {
        next[name] = inlineError;
      } else {
        delete next[name];
      }
      return next;
    });
  }

  async function save() {
    if (!draft) return;
    if (saving) return;
    setStatus("Saving...");
    setSaving(true);
    setFieldErrors({});
    setFormError("");
    const payload: Record<string, unknown> = {};
    let hasFile = false;

    try {
      fields.forEach((field) => {
        if (field.readOnly) return;
        if (field.type === "image") {
          if (files[field.name]) hasFile = true;
          return;
        }
        const type = field.type || "text";
        payload[field.name] = parseFieldValue(type, draft[field.name as keyof T]);
      });
      const validationErrors = validateTypedFields(
        fields
          .filter((field) => !field.readOnly && field.type !== "image")
          .map((field) => ({
            name: field.name,
            label: field.label,
            fieldType: field.type || "text",
            required: field.required,
            validation: field.validation,
            options: field.options?.map((option) => option.value)
          })),
        (name) => payload[name]
      );
      fields
        .filter((field) => !field.readOnly && field.type === "image" && field.required)
        .forEach((field) => {
          if (!files[field.name] && !previewUrlForField(field.name, draft)) {
            validationErrors[field.name] = "This field is required.";
          }
        });
      if (Object.keys(validationErrors).length) {
        setFieldErrors(validationErrors);
        setFormError("Please check the highlighted fields and try again.");
        toast.error("Please check the highlighted fields and try again.");
        setStatus("");
        setSaving(false);
        return;
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to prepare this form.";
      setFormError(message);
      toast.error(message);
      setStatus("");
      setSaving(false);
      return;
    }

    const finalPayload = transformPayload ? transformPayload(payload) : payload;
    const method = editingId ? "PATCH" : "POST";
    const requestPath = editingId ? `${path}${editingId}/` : path;
    const body = hasFile ? new FormData() : JSON.stringify(finalPayload);

    if (body instanceof FormData) {
      Object.entries(finalPayload).forEach(([key, value]) => {
        if (value === undefined) return;
        if (value === null) {
          body.append(key, "");
          return;
        }
        body.append(key, typeof value === "object" ? JSON.stringify(value) : String(value));
      });
      fields.forEach((field) => {
        if (field.type === "image" && files[field.name]) {
          body.append(field.name, files[field.name] as File);
        }
      });
    }

    try {
      await adminFetch<T>(requestPath, { method, body });
      setStatus("Saved.");
      toast.success(`${capitalize(itemLabel)} saved.`);
      cancel();
      await load();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to save.";
      setStatus("");
      setFormError(message);
      if (error instanceof ApiError) {
        setFieldErrors(flattenApiErrors(error.data));
      }
      toast.error(message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(item: T) {
    const confirmed = window.confirm(`Delete this ${itemLabel}?`);
    if (!confirmed) return;
    setStatus("Deleting...");
    setFormError("");
    try {
      await adminFetch<void>(`${path}${item.id}/`, { method: "DELETE" });
      setStatus("Deleted.");
      toast.success(`${capitalize(itemLabel)} deleted.`);
      await load();
    } catch (error) {
      const message = error instanceof ApiError ? formatApiError(error.data, "Unable to delete.") : error instanceof Error ? error.message : "Unable to delete.";
      setStatus("");
      setFormError(message);
      toast.error(message);
    }
  }

  return (
    <div className="grid gap-7">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-3xl text-espresso">{title}</h2>
          {status && <p className="mt-2 text-sm text-espresso/62">{status}</p>}
          {formError && <div className="mt-3 border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{formError}</div>}
        </div>
        <div className="flex gap-3">
          <button onClick={load} className="admin-button-secondary" type="button">
            <RefreshCcw size={16} />
            Refresh
          </button>
          <button onClick={startCreate} className="admin-button" type="button">
            <Plus size={16} />
            {createLabel}
          </button>
        </div>
      </div>

      {draft && (
        <section className="admin-panel">
          <div className="flex items-center justify-between gap-4 border-b border-champagne/20 pb-5">
            <h3 className="font-display text-2xl">{editingId ? `Edit ${itemLabel}` : `Create ${itemLabel}`}</h3>
            <button onClick={cancel} type="button" className="text-espresso/60 hover:text-espresso">
              <X size={20} />
            </button>
          </div>
          <div className="mt-6 grid gap-5 md:grid-cols-2">
            {fields.map((field) => (
              <FieldInput
                key={field.name}
                field={field}
                draft={draft}
                files={files}
                error={fieldErrors[field.name]}
                onChange={updateField}
                onFile={(file) => setFiles((current) => ({ ...current, [field.name]: file }))}
              />
            ))}
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <button onClick={save} disabled={saving} type="button" className="admin-button disabled:cursor-not-allowed disabled:opacity-55">
              <Save size={16} />
              {saving ? "Saving..." : "Save"}
            </button>
            <button onClick={cancel} type="button" className="admin-button-secondary">
              Cancel
            </button>
          </div>
        </section>
      )}

      <section className="overflow-hidden border border-champagne/25 bg-ivory/90 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[780px] border-collapse text-left text-sm">
            <thead className="bg-espresso text-xs uppercase tracking-[0.16em] text-ivory/72">
              <tr>
                {columns.map((column) => (
                  <th key={column.label} className="px-5 py-4 font-semibold">
                    {column.label}
                  </th>
                ))}
                <th className="px-5 py-4 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td className="px-5 py-8 text-espresso/55" colSpan={columns.length + 1}>
                    Loading {title.toLowerCase()}...
                  </td>
                </tr>
              )}
              {!loading && !items.length && (
                <tr>
                  <td className="px-5 py-8 text-espresso/55" colSpan={columns.length + 1}>
                    No {title.toLowerCase()} found.
                  </td>
                </tr>
              )}
              {!loading &&
                items.map((item) => (
                  <tr key={item.id} className="border-t border-champagne/20 bg-white/35">
                    {columns.map((column) => (
                      <td key={column.label} className="px-5 py-4 align-top text-espresso/75">
                        {column.value(item)}
                      </td>
                    ))}
                    <td className="px-5 py-4">
                      <div className="flex flex-wrap items-center gap-3">
                        <button onClick={() => startEdit(item)} type="button" className="admin-icon-link">
                          <Pencil size={15} />
                          Edit
                        </button>
                        {getEditHref && (
                          <Link href={getEditHref(item)} className="admin-icon-link">
                            <ExternalLink size={15} />
                            Open
                          </Link>
                        )}
                        {getPreviewHref && (
                          <Link href={getPreviewHref(item)} className="admin-icon-link" target="_blank">
                            <ExternalLink size={15} />
                            View
                          </Link>
                        )}
                        <button onClick={() => remove(item)} type="button" className="admin-icon-link text-red-700">
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
    </div>
  );
}

function FieldInput<T>({
  field,
  draft,
  files,
  error,
  onChange,
  onFile
}: {
  field: FieldConfig<T>;
  draft: Partial<T>;
  files: Record<string, File | null>;
  error?: string;
  onChange: (name: string, value: unknown, inlineError?: string) => void;
  onFile: (file: File | null) => void;
}) {
  const type = field.type || "text";
  const value = draft[field.name as keyof T];
  const wrapperClass = field.span === "full" || ["textarea", "json", "jsonList", "image"].includes(type) ? "md:col-span-2" : "";
  const selectedFile = files[field.name];
  const imagePreviewUrl = type === "image" ? previewUrlForField(field.name, draft) : "";
  const label = (
    <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/58">
      {field.label}
      {field.required ? " *" : ""}
      {field.readOnly ? " (read only)" : ""}
    </span>
  );

  if (type === "checkbox") {
    return (
      <div className={wrapperClass}>
        <label className="flex items-center gap-3">
          <input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(field.name, event.target.checked)} className="h-5 w-5 accent-champagne" />
          {label}
        </label>
        <FieldHelp help={field.help} error={error} />
      </div>
    );
  }

  if (type === "select") {
    return (
      <label className={wrapperClass}>
        {label}
        <select value={fieldValue(value)} onChange={(event) => onChange(field.name, event.target.value)} className="admin-input mt-2" disabled={field.readOnly}>
          <option value="">None</option>
          {field.options?.map((option) => (
            <option key={String(option.value)} value={String(option.value)}>
              {option.label}
            </option>
          ))}
        </select>
        <FieldHelp help={field.help} error={error} />
      </label>
    );
  }

  if (type === "textarea" || type === "json" || type === "jsonList") {
    return (
      <label className={wrapperClass}>
        {label}
        <textarea
          value={fieldValue(value)}
          onChange={(event) => onChange(field.name, event.target.value)}
          placeholder={field.placeholder}
          className="admin-input mt-2 min-h-32"
          disabled={field.readOnly}
        />
        <FieldHelp help={field.help} error={error} />
      </label>
    );
  }

  if (type === "image") {
    return (
      <div className={wrapperClass}>
        <label>
          {label}
          <span className="mt-2 flex min-h-28 items-center justify-center border border-dashed border-champagne/45 bg-white/55 px-4 py-5 text-sm text-espresso/60">
            <Upload size={17} className="mr-2" />
            {selectedFile ? selectedFile.name : "Upload or replace image"}
            <input type="file" accept="image/*" onChange={(event) => onFile(event.target.files?.[0] || null)} className="sr-only" />
          </span>
        </label>
        {imagePreviewUrl && (
          <div className="mt-3 flex items-center gap-4 border border-champagne/20 bg-white/50 p-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={imagePreviewUrl} alt="" className="h-20 w-20 object-cover" />
            <a href={imagePreviewUrl} target="_blank" className="text-sm font-semibold text-espresso underline underline-offset-4">
              View current image
            </a>
          </div>
        )}
        <FieldHelp help={field.help} error={error} />
      </div>
    );
  }

  return (
    <label className={wrapperClass}>
      {label}
      <input
        value={type === "datetime" ? datetimeInputValue(value) : fieldValue(value)}
        onChange={(event) => {
          if (type === "phone") {
            const next = phoneInputValue(event.target.value);
            onChange(field.name, next.value, next.error);
            return;
          }
          onChange(field.name, event.target.value);
        }}
        placeholder={field.placeholder}
        type={type === "datetime" ? "datetime-local" : type === "phone" ? "tel" : type}
        inputMode={type === "phone" ? "numeric" : type === "number" ? "decimal" : undefined}
        className="admin-input mt-2"
        disabled={field.readOnly}
      />
      <FieldHelp help={field.help} error={error} />
    </label>
  );
}

function FieldHelp({ help, error }: { help?: string; error?: string }) {
  return (
    <>
      {help && <span className="mt-2 block text-xs text-espresso/50">{help}</span>}
      {error && <span className="mt-2 block text-sm font-semibold text-red-700">{error}</span>}
    </>
  );
}

function previewUrlForField<T>(name: string, draft: Partial<T>) {
  const record = draft as Record<string, unknown>;
  const candidates = [
    `${name}_url`,
    name.replace(/_image$/, "_url"),
    name === "logo_image" ? "logo_url" : "",
    name === "favicon" ? "favicon_url" : "",
    name === "media" ? "media_url" : "",
    name === "file" ? "file_url" : ""
  ].filter(Boolean);
  for (const candidate of candidates) {
    const value = record[candidate];
    if (typeof value === "string" && value) return value;
  }
  return "";
}

function datetimeInputValue(value: unknown) {
  const raw = fieldValue(value);
  if (!raw) return "";
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw.slice(0, 16);
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
