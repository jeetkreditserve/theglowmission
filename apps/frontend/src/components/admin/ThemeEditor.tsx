"use client";

import { useEffect, useState } from "react";
import { useAdminToast } from "@/components/admin/AdminToasts";
import { ApiError, adminFetch, flattenApiErrors, formatApiError } from "@/lib/api";
import type { BrandSettings } from "@/types/cms";

type CtaStyle = {
  radius?: string;
  case?: string;
  tracking?: string;
};

const colorFields: Array<{ name: keyof BrandSettings; label: string; usage: string }> = [
  { name: "primary_color", label: "Primary / champagne", usage: "Buttons, links, borders, and highlighted labels" },
  { name: "background_color", label: "Background / ivory", usage: "Main public page background" },
  { name: "surface_color", label: "Surface / cream", usage: "Alternating sections, panels, and soft surfaces" },
  { name: "muted_color", label: "Muted / taupe", usage: "Secondary accents and subdued UI details" },
  { name: "accent_color", label: "Accent / nude", usage: "Warm supporting accent color" },
  { name: "text_color", label: "Text / espresso", usage: "Primary public text color" }
];

export function ThemeEditor() {
  const [brand, setBrand] = useState<BrandSettings | null>(null);
  const [files, setFiles] = useState<{ logo_image?: File; favicon?: File }>({});
  const [status, setStatus] = useState("");
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const toast = useAdminToast();

  useEffect(() => {
    adminFetch<BrandSettings[]>("/admin/brand-settings/")
      .then((data) => setBrand(data[0]))
      .catch(() => {
        setStatus("Sign in to edit theme settings.");
        toast.error("Sign in to edit theme settings.");
      });
  }, [toast]);

  async function save() {
    if (!brand) return;
    if (saving) return;
    setStatus("Saving...");
    setSaving(true);
    setErrors({});
    const formData = new FormData();
    const payload = {
        site_title: brand.site_title,
        tagline: brand.tagline,
        essence: brand.essence,
        mission_statement: brand.mission_statement,
        primary_color: brand.primary_color,
        background_color: brand.background_color,
        surface_color: brand.surface_color,
        muted_color: brand.muted_color,
        accent_color: brand.accent_color,
        text_color: brand.text_color,
        heading_font: brand.heading_font,
        body_font: brand.body_font,
        cta_style: brand.cta_style || {},
        contact_email: brand.contact_email,
        phone: brand.phone,
        address: brand.address,
        instagram_handle: brand.instagram_handle,
        social_links: brand.social_links || {}
      };
    Object.entries(payload).forEach(([key, value]) => formData.append(key, typeof value === "object" ? JSON.stringify(value) : String(value ?? "")));
    if (files.logo_image) formData.append("logo_image", files.logo_image);
    if (files.favicon) formData.append("favicon", files.favicon);
    try {
      const updated = await adminFetch<BrandSettings>(`/admin/brand-settings/${brand.id}/`, {
        method: "PATCH",
        body: formData
      });
      setBrand(updated);
      setFiles({});
      setStatus("Saved.");
      toast.success("Theme settings saved.");
    } catch (error) {
      const message = error instanceof ApiError ? formatApiError(error.data, "Unable to save theme settings.") : "Unable to save theme settings.";
      if (error instanceof ApiError) setErrors(flattenApiErrors(error.data));
      setStatus(message);
      toast.error(message);
    } finally {
      setSaving(false);
    }
  }

  if (!brand) {
    return <div className="border border-champagne/30 bg-ivory p-8 text-sm text-espresso/65">{status || "Loading theme settings..."}</div>;
  }

  const ctaStyle = (brand.cta_style || {}) as CtaStyle;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
      <section className="border border-champagne/30 bg-ivory p-6">
        <div className="grid gap-5">
          <TextField label="Site title" value={brand.site_title} error={errors.site_title} onChange={(value) => setBrand({ ...brand, site_title: value })} />
          <TextField label="Tagline" value={brand.tagline} error={errors.tagline} onChange={(value) => setBrand({ ...brand, tagline: value })} />
          <TextArea label="Essence" value={brand.essence} error={errors.essence} onChange={(value) => setBrand({ ...brand, essence: value })} />
          <TextArea label="Mission statement" value={brand.mission_statement} error={errors.mission_statement} onChange={(value) => setBrand({ ...brand, mission_statement: value })} />
          <div className="grid gap-5 md:grid-cols-2">
            <TextField label="Heading font" value={brand.heading_font} error={errors.heading_font} onChange={(value) => setBrand({ ...brand, heading_font: value })} />
            <TextField label="Body font" value={brand.body_font} error={errors.body_font} onChange={(value) => setBrand({ ...brand, body_font: value })} />
          </div>
          <div className="grid gap-5 md:grid-cols-2">
            <FileField label="Logo image" onChange={(file) => setFiles((current) => ({ ...current, logo_image: file }))} />
            <FileField label="Favicon" onChange={(file) => setFiles((current) => ({ ...current, favicon: file }))} />
          </div>
          <div className="grid gap-5 md:grid-cols-2">
            <TextField label="Email" value={brand.contact_email} error={errors.contact_email} onChange={(value) => setBrand({ ...brand, contact_email: value })} />
            <TextField label="Phone" value={brand.phone} error={errors.phone} onChange={(value) => setBrand({ ...brand, phone: value })} />
            <TextField label="Instagram" value={brand.instagram_handle} error={errors.instagram_handle} onChange={(value) => setBrand({ ...brand, instagram_handle: value })} />
          </div>
          <TextArea label="Address" value={brand.address} error={errors.address} onChange={(value) => setBrand({ ...brand, address: value })} />
          <button onClick={save} disabled={saving} className="brand-button w-fit bg-champagne px-7 py-4 text-sm font-semibold text-espresso disabled:cursor-not-allowed disabled:opacity-55">
            {saving ? "Saving..." : "Save theme"}
          </button>
          {status && <p className="text-sm text-espresso/62">{status}</p>}
        </div>
      </section>
      <section className="border border-champagne/30 bg-cream p-6">
        <h2 className="font-display text-2xl">Palette</h2>
        <div className="mt-6 grid gap-4">
          {colorFields.map((field) => (
            <label key={field.name} className="grid gap-3 border border-champagne/20 bg-ivory p-3">
              <span>
                <span className="block text-xs font-semibold uppercase tracking-[0.14em] text-espresso/70">{field.label}</span>
                <span className="mt-1 block text-xs leading-5 text-espresso/55">{field.usage}</span>
              </span>
              <span className="flex items-center gap-3">
                <input type="color" value={String(brand[field.name])} onChange={(event) => setBrand({ ...brand, [field.name]: event.target.value })} />
                <span className="font-mono text-sm">{String(brand[field.name])}</span>
              </span>
            </label>
          ))}
        </div>
        <div className="mt-8 border-t border-champagne/25 pt-6">
          <h2 className="font-display text-2xl">CTA Style</h2>
          <div className="mt-5 grid gap-4">
            <TextField label="Button radius" value={ctaStyle.radius || "2px"} onChange={(value) => setBrand({ ...brand, cta_style: { ...ctaStyle, radius: value } })} />
            <TextField label="Letter spacing" value={ctaStyle.tracking || "0.12em"} onChange={(value) => setBrand({ ...brand, cta_style: { ...ctaStyle, tracking: value } })} />
            <SelectField label="Text transform" value={ctaStyle.case || "uppercase"} onChange={(value) => setBrand({ ...brand, cta_style: { ...ctaStyle, case: value } })} />
          </div>
        </div>
      </section>
    </div>
  );
}

function TextField({ label, value, error, onChange }: { label: string; value: string; error?: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/62">{label}</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 w-full border border-champagne/35 bg-white px-4 py-3 outline-none focus:border-champagne" />
      {error && <span className="mt-2 block text-sm font-semibold text-red-700">{error}</span>}
    </label>
  );
}

function TextArea({ label, value, error, onChange }: { label: string; value: string; error?: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/62">{label}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 min-h-28 w-full border border-champagne/35 bg-white px-4 py-3 outline-none focus:border-champagne" />
      {error && <span className="mt-2 block text-sm font-semibold text-red-700">{error}</span>}
    </label>
  );
}

function FileField({ label, onChange }: { label: string; onChange: (file: File | undefined) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/62">{label}</span>
      <input type="file" accept="image/*" onChange={(event) => onChange(event.target.files?.[0])} className="mt-2 w-full border border-champagne/35 bg-white px-4 py-3 text-sm outline-none focus:border-champagne" />
    </label>
  );
}

function SelectField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/62">{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 w-full border border-champagne/35 bg-white px-4 py-3 outline-none focus:border-champagne">
        <option value="uppercase">Uppercase</option>
        <option value="none">None</option>
        <option value="capitalize">Capitalize</option>
        <option value="lowercase">Lowercase</option>
      </select>
    </label>
  );
}
