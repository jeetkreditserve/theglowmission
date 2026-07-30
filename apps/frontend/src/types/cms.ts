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
  canonical_site_url: string;
  seo_title: string;
  seo_description: string;
  business_description: string;
  area_served: string;
  same_as_links: string[];
  opening_hours: string[];
  latitude: string | null;
  longitude: string | null;
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
  eyebrow: string;
  title: string;
  subtitle: string;
  body: string;
  media_url: string | null;
  media_variants?: ImageVariantSet;
  media_alt: string;
  cta_label: string;
  cta_url: string;
  cta_style: string;
  secondary_cta_label: string;
  secondary_cta_url: string;
  secondary_cta_style: string;
  layout_variant: string;
  background_variant: string;
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
  schedule_enabled: boolean;
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
  calendly_event_url: string;
  duration_minutes?: number | null;
  booking_buffer_minutes?: number | null;
  accepts_online_booking?: boolean;
  calendly_fallback_enabled?: boolean;
  booking_campaign: number | null;
  booking_campaign_slug: string;
  active: boolean;
  ordering: number;
};

export type PublicAppFeatureFlags = {
  customer_registration?: boolean;
  customer_password_reset?: boolean;
  customer_notifications?: boolean;
  web_push?: boolean;
  native_push?: boolean;
  calendly_booking?: boolean;
  first_party_scheduling?: boolean;
};

export type PublicAppConfig = {
  schema_version: number;
  generated_at: string;
  content_version: string;
  feature_flags: PublicAppFeatureFlags;
};

export type AvailableSlot = {
  starts_at: string;
  ends_at: string;
  label?: string;
};

export type AvailableSlotsResponse =
  | AvailableSlot[]
  | {
      date: string;
      service?: Service | number | string;
      slots: AvailableSlot[];
    };

export type PublicAppointmentDraft = {
  full_name: string;
  phone: string;
  email?: string;
  skin_goal?: string;
  customer_notes?: string;
  starts_at: string;
};

export type AppointmentStatus = "confirmed" | "completed" | "cancelled" | "no_show";

export type Appointment = {
  id: number;
  service: number | null;
  service_title?: string;
  service_slug?: string;
  contact: number | null;
  contact_display_name?: string;
  full_name: string;
  phone: string;
  email: string;
  skin_goal: string;
  customer_notes: string;
  starts_at: string;
  ends_at: string;
  status: AppointmentStatus | string;
  source?: string;
  photos?: AppointmentPhoto[];
  photo_count?: number;
  visible_photo_count?: number;
  created_at: string;
  updated_at?: string;
};

export type AppointmentPhoto = {
  id: number;
  appointment: number;
  image_url: string | null;
  image_key?: string | null;
  photo_type?: "before" | "after" | string;
  notes?: string;
  created_by_email?: string;
  created_at?: string;
  updated_at?: string;
};

export type AppointmentAvailabilityWindow = {
  id: number;
  weekday: number;
  starts_at: string;
  ends_at: string;
  active: boolean;
  label?: string;
  ordering?: number;
};

export type AppointmentAvailabilityImpactAppointment = {
  id: number;
  full_name: string;
  service_title: string;
  starts_at: string;
  ends_at: string;
  status: string;
};

export type AppointmentAvailabilityImpact = {
  affected_count: number;
  appointments: AppointmentAvailabilityImpactAppointment[];
};

export type AppointmentBlock = {
  id: number;
  starts_at: string;
  ends_at: string;
  reason: string;
  active: boolean;
};

export type SeoIndexItem = {
  path: string;
  title: string;
  description: string;
  type: "page" | "service" | "campaign";
  updated_at: string;
  priority: number;
  image_url: string | null;
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
  is_anonymized: boolean;
  active: boolean;
  ordering: number;
};

export type SiteNavigationItem = {
  id: number;
  label: string;
  url: string;
  placement: "header" | "header_cta" | "footer" | "footer_cta" | "footer_contact" | "social";
  style: "link" | "primary" | "secondary" | "muted";
  open_in_new_tab: boolean;
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
  submitting_label: string;
  empty_select_label: string;
  checkbox_label: string;
  error_message: string;
  schedule_enabled?: boolean;
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

export type ContactStatus = {
  id: number;
  name: string;
  slug: string;
  ordering: number;
  is_default: boolean;
  contact_count: number;
  updated_at: string;
};

export type ContactSummary = {
  id: number;
  display_name: string;
  full_name: string;
  email: string;
  phone: string;
  status: number | null;
  status_name: string;
  marketing_consent: boolean;
  last_activity_at: string | null;
  source_response_count: number;
  is_merged: boolean;
};

export type ContactAuditEvent = {
  id: number;
  event_type: string;
  field_name: string;
  old_value: unknown;
  new_value: unknown;
  source_type: string;
  source_id: string;
  actor_email: string;
  message: string;
  created_at: string;
};

export type ContactNote = {
  id: number;
  contact: number;
  body: string;
  created_by_email: string;
  created_at: string;
  updated_at: string;
};

export type Contact = ContactSummary & {
  address: string;
  age: number | null;
  skin_type: string;
  preferred_ritual: string;
  preferred_day: string;
  skin_goal: string;
  first_activity_at: string | null;
  merged_into: number | null;
  merged_at: string | null;
  possible_duplicate_count: number;
  possible_duplicates: ContactSummary[];
  notes: ContactNote[];
  audit_events: ContactAuditEvent[];
  history_entries?: ContactHistoryEntry[];
  appointments?: Appointment[];
  appointment_count?: number;
  completed_appointment_count?: number;
  photo_count?: number;
  created_at: string;
  updated_at: string;
};

export type ContactHistoryEntry = {
  id: number;
  contact: number;
  contact_display_name?: string;
  appointment?: number | null;
  appointment_starts_at?: string | null;
  appointment_status?: string | null;
  event_at: string;
  service_label: string;
  amount?: string | null;
  notes: string;
  before_photo?: number | null;
  before_photo_url?: string | null;
  before_photo_key?: string | null;
  after_photo?: number | null;
  after_photo_url?: string | null;
  after_photo_key?: string | null;
  created_by_email?: string;
  created_at?: string;
  updated_at?: string;
};

export type FounderDashboardMetric = {
  key: string;
  label: string;
  value: number | string;
  change?: number | string | null;
  description?: string;
};

export type FounderDashboardResponse = {
  period: string;
  generated_at?: string;
  headline_metrics?: FounderDashboardMetric[] | Record<string, number | string | FounderDashboardMetric>;
  metrics?: FounderDashboardMetric[] | Record<string, number | string | FounderDashboardMetric>;
  appointments?: Appointment[];
  recent_contacts?: ContactSummary[];
  recent_history?: ContactHistoryEntry[];
  notifications?: NotificationCampaign[];
  [key: string]: unknown;
};

export type NotificationCampaignStatus = "draft" | "scheduled" | "sent" | "cancelled" | string;

export type NotificationCampaign = {
  id: number;
  title: string;
  subject: string;
  body: string;
  target_status?: number | null;
  marketing_consent_only?: boolean;
  include_customers?: boolean;
  status: NotificationCampaignStatus;
  recipient_count?: number;
  message_log_count?: number;
  scheduled_at?: string | null;
  sent_at?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type NotificationCampaignRecipient = {
  id?: number;
  contact?: number | null;
  user?: number | null;
  display_name?: string;
  email?: string;
  phone?: string;
  created_at?: string;
};
