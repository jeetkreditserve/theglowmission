import type { CSSProperties, ReactNode } from "react";
import type { BrandSettings } from "@/types/cms";

type ThemeStyle = CSSProperties & Record<`--${string}`, string>;

const fallbackColors = {
  background: "#FBF4EA",
  surface: "#F4E7D8",
  primary: "#C9A46A",
  muted: "#BBA08E",
  accent: "#D8C7A4",
  text: "#251D18",
  sage: "#82947A",
  rose: "#CFAE9E"
};

export function BrandTheme({ brand, children }: { brand: BrandSettings; children: ReactNode }) {
  const ctaStyle = brand.cta_style || {};
  const style: ThemeStyle = {
    "--color-ivory": normalizeHex(brand.background_color, fallbackColors.background),
    "--color-ivory-rgb": hexToRgbTriplet(brand.background_color, fallbackColors.background),
    "--color-cream": normalizeHex(brand.surface_color, fallbackColors.surface),
    "--color-cream-rgb": hexToRgbTriplet(brand.surface_color, fallbackColors.surface),
    "--color-champagne": normalizeHex(brand.primary_color, fallbackColors.primary),
    "--color-champagne-rgb": hexToRgbTriplet(brand.primary_color, fallbackColors.primary),
    "--color-taupe": normalizeHex(brand.muted_color, fallbackColors.muted),
    "--color-taupe-rgb": hexToRgbTriplet(brand.muted_color, fallbackColors.muted),
    "--color-nude": normalizeHex(brand.accent_color, fallbackColors.accent),
    "--color-nude-rgb": hexToRgbTriplet(brand.accent_color, fallbackColors.accent),
    "--color-espresso": normalizeHex(brand.text_color, fallbackColors.text),
    "--color-espresso-rgb": hexToRgbTriplet(brand.text_color, fallbackColors.text),
    "--color-sage": fallbackColors.sage,
    "--color-sage-rgb": hexToRgbTriplet(fallbackColors.sage, fallbackColors.sage),
    "--color-rose": fallbackColors.rose,
    "--color-rose-rgb": hexToRgbTriplet(fallbackColors.rose, fallbackColors.rose),
    "--font-display": fontStack(brand.heading_font, '"Cormorant Garamond", Georgia, serif'),
    "--font-body": fontStack(brand.body_font, '"Montserrat", Lato, Arial, sans-serif'),
    "--cta-radius": typeof ctaStyle.radius === "string" ? ctaStyle.radius : "2px",
    "--cta-tracking": typeof ctaStyle.tracking === "string" ? ctaStyle.tracking : "0.12em",
    "--cta-case": typeof ctaStyle.case === "string" ? ctaStyle.case : "uppercase"
  };

  return (
    <div style={style} className="min-h-screen bg-ivory text-espresso">
      {children}
    </div>
  );
}

function normalizeHex(value: string | null | undefined, fallback: string) {
  const raw = value?.trim();
  return raw && /^#[0-9a-fA-F]{6}$/.test(raw) ? raw : fallback;
}

function hexToRgbTriplet(value: string | null | undefined, fallback: string) {
  const hex = normalizeHex(value, fallback).replace("#", "");
  const red = Number.parseInt(hex.slice(0, 2), 16);
  const green = Number.parseInt(hex.slice(2, 4), 16);
  const blue = Number.parseInt(hex.slice(4, 6), 16);
  return `${red} ${green} ${blue}`;
}

function fontStack(font: string | null | undefined, fallback: string) {
  const trimmed = font?.trim();
  if (!trimmed) return fallback;
  return trimmed.includes(",") ? trimmed : `"${trimmed}", ${fallback}`;
}
