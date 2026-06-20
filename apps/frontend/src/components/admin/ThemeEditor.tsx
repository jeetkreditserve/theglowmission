"use client";

import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/api";
import type { BrandSettings } from "@/types/cms";

const colorFields: Array<keyof BrandSettings> = ["primary_color", "background_color", "surface_color", "muted_color", "accent_color", "text_color"];

export function ThemeEditor() {
  const [brand, setBrand] = useState<BrandSettings | null>(null);
  const [files, setFiles] = useState<{ logo_image?: File; favicon?: File }>({});
  const [status, setStatus] = useState("");

  useEffect(() => {
    adminFetch<BrandSettings[]>("/admin/brand-settings/").then((data) => setBrand(data[0])).catch(() => setStatus("Sign in to edit theme settings."));
  }, []);

  async function save() {
    if (!brand) return;
    setStatus("Saving...");
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
        contact_email: brand.contact_email,
        phone: brand.phone,
        address: brand.address,
        instagram_handle: brand.instagram_handle,
        social_links: brand.social_links || {}
      };
    Object.entries(payload).forEach(([key, value]) => formData.append(key, typeof value === "object" ? JSON.stringify(value) : String(value ?? "")));
    if (files.logo_image) formData.append("logo_image", files.logo_image);
    if (files.favicon) formData.append("favicon", files.favicon);
    const updated = await adminFetch<BrandSettings>(`/admin/brand-settings/${brand.id}/`, {
      method: "PATCH",
      body: formData
    });
    setBrand(updated);
    setFiles({});
    setStatus("Saved.");
  }

  if (!brand) {
    return <div className="border border-champagne/30 bg-ivory p-8 text-sm text-espresso/65">{status || "Loading theme settings..."}</div>;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
      <section className="border border-champagne/30 bg-ivory p-6">
        <div className="grid gap-5">
          <TextField label="Site title" value={brand.site_title} onChange={(value) => setBrand({ ...brand, site_title: value })} />
          <TextField label="Tagline" value={brand.tagline} onChange={(value) => setBrand({ ...brand, tagline: value })} />
          <TextArea label="Essence" value={brand.essence} onChange={(value) => setBrand({ ...brand, essence: value })} />
          <TextArea label="Mission statement" value={brand.mission_statement} onChange={(value) => setBrand({ ...brand, mission_statement: value })} />
          <div className="grid gap-5 md:grid-cols-2">
            <FileField label="Logo image" onChange={(file) => setFiles((current) => ({ ...current, logo_image: file }))} />
            <FileField label="Favicon" onChange={(file) => setFiles((current) => ({ ...current, favicon: file }))} />
          </div>
          <div className="grid gap-5 md:grid-cols-2">
            <TextField label="Email" value={brand.contact_email} onChange={(value) => setBrand({ ...brand, contact_email: value })} />
            <TextField label="Phone" value={brand.phone} onChange={(value) => setBrand({ ...brand, phone: value })} />
            <TextField label="Instagram" value={brand.instagram_handle} onChange={(value) => setBrand({ ...brand, instagram_handle: value })} />
          </div>
          <TextArea label="Address" value={brand.address} onChange={(value) => setBrand({ ...brand, address: value })} />
          <button onClick={save} className="w-fit bg-champagne px-7 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-white">
            Save theme
          </button>
          {status && <p className="text-sm text-espresso/62">{status}</p>}
        </div>
      </section>
      <section className="border border-champagne/30 bg-cream p-6">
        <h2 className="font-display text-2xl">Palette</h2>
        <div className="mt-6 grid gap-4">
          {colorFields.map((field) => (
            <label key={field} className="flex items-center justify-between gap-4 border border-champagne/20 bg-ivory p-3">
              <span className="text-xs font-semibold uppercase tracking-[0.14em] text-espresso/60">{field.replace("_", " ")}</span>
              <span className="flex items-center gap-3">
                <input type="color" value={String(brand[field])} onChange={(event) => setBrand({ ...brand, [field]: event.target.value })} />
                <span className="font-mono text-sm">{String(brand[field])}</span>
              </span>
            </label>
          ))}
        </div>
      </section>
    </div>
  );
}

function TextField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/62">{label}</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 w-full border border-champagne/35 bg-white px-4 py-3 outline-none focus:border-champagne" />
    </label>
  );
}

function TextArea({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.16em] text-espresso/62">{label}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 min-h-28 w-full border border-champagne/35 bg-white px-4 py-3 outline-none focus:border-champagne" />
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
