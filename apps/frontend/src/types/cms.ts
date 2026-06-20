export type ImageVariant = {
  url: string | null;
  key: string;
  width: number;
  height: number;
  format: "webp" | "jpeg";
  byte_size: number;
};

export type ImageVariantSet = {
  webp: ImageVariant[];
  jpeg: ImageVariant[];
  fallback_url: string | null;
  fallback_key: string | null;
};

export type BrandSettings = {
  id: number;
  site_title: string;
  tagline: string;
  essence: string;
  mission_statement: string;
  logo_url: string | null;
  logo_key: string | null;
  logo_variants?: ImageVariantSet;
  favicon_url: string | null;
  favicon_key: string | null;
  favicon_variants?: ImageVariantSet;
  primary_color: string;
  background_color: string;
  surface_color: string;
  muted_color: string;
  accent_color: string;
  text_color: string;
  heading_font: string;
  body_font: string;
  cta_style: Record<string, unknown>;
  contact_email: string;
  phone: string;
  address: string;
  instagram_handle: string;
  social_links: Record<string, string>;
};

export type PageSection = {
  id: number;
  section_type: "hero" | "story" | "services" | "gallery" | "testimonials" | "faqs" | "cta" | "rich_text";
  title: string;
  subtitle: string;
  body: string;
  media_url: string | null;
  media_variants?: ImageVariantSet;
  cta_label: string;
  cta_url: string;
  ordering: number;
  active: boolean;
  config: Record<string, unknown>;
};

export type HeroSlide = {
  id: number;
  title: string;
  subtitle: string;
  body: string;
  image_url: string | null;
  image_variants?: ImageVariantSet;
  image_alt: string;
  offer_label: string;
  primary_cta_label: string;
  primary_cta_url: string;
  secondary_cta_label: string;
  secondary_cta_url: string;
  linked_campaign: number | null;
  campaign_slug: string;
  campaign_title: string;
  starts_at: string | null;
  ends_at: string | null;
  active: boolean;
  is_active_now: boolean;
  ordering: number;
  config: Record<string, unknown>;
};

export type Page = {
  id: number;
  title: string;
  slug: string;
  status: string;
  seo_title: string;
  seo_description: string;
  ordering: number;
  sections: PageSection[];
};

export type Service = {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  description: string;
  image_url: string | null;
  image_variants?: ImageVariantSet;
  image_alt: string;
  duration: string;
  session_count: number;
  currency: string;
  price_amount: string | null;
  sale_price_amount: string | null;
  discount_label: string;
  price_note: string;
  inclusions: string[];
  featured: boolean;
  cta_label: string;
  cta_url: string;
  booking_campaign: number | null;
  booking_campaign_slug: string;
  active: boolean;
  ordering: number;
};

export type GalleryImage = {
  id: number;
  title: string;
  alt_text: string;
  image_url: string | null;
  image_variants?: ImageVariantSet;
  caption: string;
  active: boolean;
  ordering: number;
};

export type FAQ = {
  id: number;
  question: string;
  answer: string;
  active: boolean;
  ordering: number;
};

export type Testimonial = {
  id: number;
  name: string;
  quote: string;
  role: string;
  active: boolean;
  ordering: number;
};

export type CampaignField = {
  id: number;
  label: string;
  key: string;
  field_type: "text" | "textarea" | "email" | "phone" | "select" | "checkbox" | "radio" | "date" | "number";
  placeholder: string;
  help_text: string;
  required: boolean;
  options: string[];
  validation: Record<string, unknown>;
  ordering: number;
};

export type CampaignForm = {
  id: number;
  title: string;
  slug: string;
  status?: string;
  summary: string;
  offer_label: string;
  hero_image_url: string | null;
  hero_image_variants?: ImageVariantSet;
  hero_image_alt: string;
  button_label: string;
  starts_at?: string | null;
  ends_at?: string | null;
  success_message: string;
  redirect_url: string;
  seo_title: string;
  seo_description: string;
  fields: CampaignField[];
  response_count?: number;
  is_active_now?: boolean;
};
