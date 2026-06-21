import type { BrandSettings, CampaignForm, FAQ, GalleryImage, HeroSlide, Page, SeoIndexItem, Service, SiteNavigationItem, Testimonial } from "@/types/cms";

const serverBaseUrl = process.env.INTERNAL_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://backend:8000/api/v1";
const browserBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "/api/v1";

export class ApiError extends Error {
  status: number;
  path: string;
  data: unknown;

  constructor(message: string, status: number, path: string, data: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.path = path;
    this.data = data;
  }
}

export function apiBaseUrl() {
  return typeof window === "undefined" ? serverBaseUrl : browserBaseUrl;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!(init?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers,
    cache: "no-store"
  });
  if (!response.ok) {
    const data = await readResponseBody(response);
    throw new ApiError(formatApiError(data, `API request failed: ${response.status}`), response.status, path, data);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function getBrandSettings() {
  return apiFetch<BrandSettings>("/public/brand-settings/");
}

export async function getPage(slug: string) {
  return apiFetch<Page>(`/public/pages/${slug}/`);
}

export async function getHeroSlides() {
  return apiFetch<HeroSlide[]>("/public/hero-slides/");
}

export async function getServices() {
  return apiFetch<Service[]>("/public/services/");
}

export async function getService(slug: string) {
  return apiFetch<Service>(`/public/services/${slug}/`);
}

export async function getSeoIndex() {
  return apiFetch<SeoIndexItem[]>("/public/seo-index/");
}

export async function getGallery() {
  return apiFetch<GalleryImage[]>("/public/gallery/");
}

export async function getFAQs() {
  return apiFetch<FAQ[]>("/public/faqs/");
}

export async function getTestimonials() {
  return apiFetch<Testimonial[]>("/public/testimonials/");
}

export async function getNavigationItems() {
  return apiFetch<SiteNavigationItem[]>("/public/navigation-items/");
}

export async function getCampaignForm(slug: string) {
  return apiFetch<CampaignForm>(`/public/campaign-forms/${slug}/`);
}

export async function submitCampaignResponse(slug: string, responseData: Record<string, unknown>) {
  return apiFetch<{ id: number; message: string; redirect_url: string }>(`/public/campaign-forms/${slug}/responses/`, {
    method: "POST",
    body: JSON.stringify({ response_data: responseData })
  });
}

export function authHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? window.localStorage.getItem("glow_admin_token") : null;
  return token ? { Authorization: `Token ${token}` } : {};
}

export async function adminFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!(init?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  Object.entries(authHeaders()).forEach(([key, value]) => headers.set(key, value));
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers
  });
  if (response.status === 401 || response.status === 403) {
    throw new Error("AUTH_REQUIRED");
  }
  if (!response.ok) {
    const data = await readResponseBody(response);
    throw new ApiError(formatApiError(data, `Admin API request failed: ${response.status}`), response.status, path, data);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

async function readResponseBody(response: Response): Promise<unknown | null> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

export function formatApiError(data: unknown, fallback = "Something went wrong."): string {
  if (!data) return fallback;
  if (typeof data === "string") return data;
  if (Array.isArray(data)) return data.map((item) => formatApiError(item, "")).filter(Boolean).join(" ");
  if (typeof data === "object") {
    const record = data as Record<string, unknown>;
    if (typeof record.detail === "string") return record.detail;
    if (typeof record.error === "string") return record.error;
    if (Array.isArray(record.non_field_errors)) return record.non_field_errors.join(" ");
    const [firstKey, firstValue] = Object.entries(record)[0] || [];
    if (firstKey) {
      const valueMessage = formatApiError(firstValue, "");
      return valueMessage ? `${humanizeKey(firstKey)}: ${valueMessage}` : fallback;
    }
  }
  return fallback;
}

export function flattenApiErrors(data: unknown): Record<string, string> {
  if (!data || typeof data !== "object" || Array.isArray(data)) return {};
  return Object.fromEntries(
    Object.entries(data as Record<string, unknown>).map(([key, value]) => [key, formatApiError(value, "Invalid value.")])
  );
}

function humanizeKey(key: string): string {
  if (key === "non_field_errors") return "Form";
  return key.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function fallbackBrand(): BrandSettings {
  return {
    id: 1,
    site_title: "The Glow Mission",
    tagline: "Glow, the natural way.",
    essence: "Soft. Elegant. Timeless. Made to make you glow.",
    mission_statement:
      "A mission of care, confidence, visible glow, and natural beauty. Every ritual is shaped around natural ingredients, facial massage, sculpting touch, and calming skin care.",
    canonical_site_url: "https://theglowmission.com",
    seo_title: "The Glow Mission | Natural Facial Rituals in Chandivali, Powai",
    seo_description:
      "The Glow Mission is a boutique facial wellness studio in Chandivali and Powai, Mumbai, offering natural facial rituals, facial massage, face yoga, gua sha, and glow treatments.",
    business_description:
      "The Glow Mission is a boutique facial wellness studio built around natural ingredients, facial massage, face yoga, lifting techniques, calming rituals, and visible glow.",
    area_served: "Chandivali, Powai, Mumbai, India",
    same_as_links: ["https://instagram.com/the.glow.mission"],
    opening_hours: [],
    latitude: null,
    longitude: null,
    logo_url: null,
    logo_key: null,
    favicon_url: null,
    favicon_key: null,
    primary_color: "#D9B88C",
    background_color: "#FFF7F0",
    surface_color: "#F6EEE4",
    muted_color: "#CDB8A9",
    accent_color: "#E6D6C6",
    text_color: "#2B2623",
    heading_font: "Cinzel",
    body_font: "Montserrat",
    cta_style: { radius: "2px", case: "uppercase", tracking: "0.12em" },
    contact_email: "info@theglowmission.com",
    phone: "",
    address: "",
    instagram_handle: "@the.glow.mission",
    social_links: {}
  };
}
