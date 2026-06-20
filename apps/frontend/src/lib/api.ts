import type { BrandSettings, CampaignForm, FAQ, GalleryImage, HeroSlide, Page, Service, Testimonial } from "@/types/cms";

const serverBaseUrl = process.env.INTERNAL_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://backend:8000/api/v1";
const browserBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "/api/v1";

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
    throw new Error(`API request failed: ${response.status} ${path}`);
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

export async function getGallery() {
  return apiFetch<GalleryImage[]>("/public/gallery/");
}

export async function getFAQs() {
  return apiFetch<FAQ[]>("/public/faqs/");
}

export async function getTestimonials() {
  return apiFetch<Testimonial[]>("/public/testimonials/");
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
    throw new Error(`Admin API request failed: ${response.status} ${path}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export function fallbackBrand(): BrandSettings {
  return {
    id: 1,
    site_title: "The Glow Mission",
    tagline: "Glow, the natural way.",
    essence: "Soft. Elegant. Timeless. Made to make you glow.",
    mission_statement:
      "A mission of care, confidence, visible glow, and natural beauty. Every session is one peaceful hour of natural ingredients, face yoga, facial massage, lifting techniques, and calming rituals.",
    logo_url: "/reference/glow-mission-logo-3d.png",
    logo_key: null,
    favicon_url: "/reference/glow-mission-logo-3d.png",
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
    contact_email: "hello@theglowmission.com",
    phone: "",
    address: "",
    instagram_handle: "@theglowmission",
    social_links: {}
  };
}

export const fallbackServices: Service[] = [
  {
    id: 1,
    title: "Signature Glow Ritual",
    slug: "signature-glow-ritual",
    short_description: "A one-hour facial massage and natural glow ritual for rested, brighter-looking skin.",
    description: "Calming touch, natural textures, and a slow visible glow.",
    image_url: null,
    image_alt: "Signature Glow Ritual treatment",
    duration: "60 minutes",
    session_count: 1,
    currency: "INR",
    price_amount: "2500.00",
    sale_price_amount: "1999.00",
    discount_label: "Introductory glow price",
    price_note: "Introductory pricing available",
    inclusions: ["Facial massage", "Botanical mask", "Glow finish"],
    featured: true,
    cta_label: "Book this ritual",
    cta_url: "/campaigns/glow-consultation",
    booking_campaign: null,
    booking_campaign_slug: "glow-consultation",
    active: true,
    ordering: 0
  },
  {
    id: 2,
    title: "Face Yoga Lift",
    slug: "face-yoga-lift",
    short_description: "Guided face yoga and lifting massage to soften tension and support natural contour.",
    description: "Designed for facial tension, softness, and natural lift.",
    image_url: null,
    image_alt: "Face Yoga Lift treatment",
    duration: "45 minutes",
    session_count: 1,
    currency: "INR",
    price_amount: "1800.00",
    sale_price_amount: null,
    discount_label: "",
    price_note: "Available as an add-on",
    inclusions: ["Face yoga", "Lifting massage", "Jaw release"],
    featured: false,
    cta_label: "Book this ritual",
    cta_url: "/campaigns/glow-consultation",
    booking_campaign: null,
    booking_campaign_slug: "glow-consultation",
    active: true,
    ordering: 1
  },
  {
    id: 3,
    title: "Natural Ingredient Facial",
    slug: "natural-ingredient-facial",
    short_description: "A gentle ritual inspired by honey, citrus, cucumber, and cream.",
    description: "A soft, sensory ritual for calm and brightness.",
    image_url: null,
    image_alt: "Natural Ingredient Facial treatment",
    duration: "60 minutes",
    session_count: 1,
    currency: "INR",
    price_amount: "2200.00",
    sale_price_amount: null,
    discount_label: "Seasonal ritual",
    price_note: "Seasonal ritual",
    inclusions: ["Natural ingredients", "Cooling compress", "Hydrating finish"],
    featured: false,
    cta_label: "Book this ritual",
    cta_url: "/campaigns/glow-consultation",
    booking_campaign: null,
    booking_campaign_slug: "glow-consultation",
    active: true,
    ordering: 2
  }
];
