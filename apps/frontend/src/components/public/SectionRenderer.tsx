import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowRight, Check, ChevronDown, Instagram, Mail, MapPin, Phone, Quote } from "lucide-react";
import type { BrandSettings, FAQ, GalleryImage, PageSection, Service, Testimonial } from "@/types/cms";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";
import { RitualBookingButton } from "@/components/public/RitualBookingButton";

export function SectionRenderer({
  sections,
  services,
  gallery,
  faqs,
  testimonials,
  brand,
  includeHeroSections = false
}: {
  sections: PageSection[];
  services: Service[];
  gallery: GalleryImage[];
  faqs: FAQ[];
  testimonials: Testimonial[];
  brand?: BrandSettings;
  includeHeroSections?: boolean;
}) {
  const visible = sections.filter((section) => includeHeroSections || section.section_type !== "hero");

  return (
    <>
      {visible.map((section, index) => {
        if (section.section_type === "hero") return <HeroSection key={section.id} section={section} />;
        if (section.section_type === "services") return <ServiceBand key={section.id} section={section} services={services} />;
        if (section.section_type === "gallery") return <GalleryBand key={section.id} section={section} gallery={gallery} />;
        if (section.section_type === "testimonials") return <TestimonialBand key={section.id} section={section} testimonials={testimonials} />;
        if (section.section_type === "faqs") return <FAQBand key={section.id} section={section} faqs={faqs} />;
        if (section.section_type === "cta") return <CtaBand key={section.id} section={section} />;
        if (section.layout_variant === "contact_details") return <ContactBand key={section.id} section={section} brand={brand} />;
        return <StoryBand key={section.id} section={section} flip={index % 2 === 1} />;
      })}
    </>
  );
}

function HeroSection({ section }: { section: PageSection }) {
  return (
    <section className="relative overflow-hidden bg-espresso px-5 py-24 text-ivory md:py-32 lg:px-8">
      {section.media_url && (
        <>
          <ResponsiveImage
            src={section.media_url}
            variants={section.media_variants}
            alt={section.media_alt || section.title}
            sizes="100vw"
            loading="eager"
            fetchPriority="high"
            decoding="async"
            className="absolute inset-0 h-full w-full object-cover opacity-[0.42]"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-espresso via-espresso/80 to-espresso/24" />
        </>
      )}
      <div className="relative mx-auto max-w-7xl">
        {sectionEyebrow(section) && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{sectionEyebrow(section)}</p>}
        <h1 className="mt-5 max-w-4xl font-display text-5xl leading-tight md:text-7xl">{section.title}</h1>
        {section.subtitle && <p className="mt-7 max-w-2xl text-lg leading-9 text-ivory/72">{section.subtitle}</p>}
        {section.body && <p className="mt-4 max-w-2xl text-base leading-8 text-ivory/66">{section.body}</p>}
        <SectionCtas section={section} tone="dark" />
      </div>
    </section>
  );
}

function StoryBand({ section, flip }: { section: PageSection; flip?: boolean }) {
  const hasMedia = Boolean(section.media_url);
  return (
    <section className={section.background_variant === "cream" ? "bg-cream py-24 md:py-32" : "bg-ivory py-24 md:py-32"}>
      <div className={`mx-auto grid max-w-7xl items-center gap-14 px-5 lg:px-8 ${hasMedia ? "md:grid-cols-[0.95fr_1.05fr]" : ""} ${flip ? "md:[&>*:first-child]:order-2" : ""}`}>
        <div>
          {sectionEyebrow(section) && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{sectionEyebrow(section)}</p>}
          {section.title && <h2 className="mt-5 max-w-2xl font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>}
          {section.subtitle && <p className="mt-5 max-w-2xl text-lg leading-8 text-espresso/64">{section.subtitle}</p>}
          {section.body && <p className="mt-7 max-w-2xl text-base leading-8 text-espresso/68">{section.body}</p>}
          <SectionCtas section={section} />
        </div>
        {hasMedia && (
          <figure className="relative">
            <div className="absolute -left-5 -top-5 h-full w-full border border-champagne/35" />
            <ResponsiveImage
              src={section.media_url}
              variants={section.media_variants}
              alt={section.media_alt || section.title}
              sizes="(min-width: 768px) 50vw, 100vw"
              loading="lazy"
              decoding="async"
              className="relative aspect-[4/5] w-full object-cover shadow-[0_34px_90px_rgba(37,29,24,0.18)]"
            />
          </figure>
        )}
      </div>
    </section>
  );
}

function ServiceBand({ section, services }: { section: PageSection; services: Service[] }) {
  return (
    <section className="bg-[#211915] py-24 text-ivory md:py-32">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="grid gap-8 md:grid-cols-[0.8fr_1.2fr] md:items-end">
          <div>
            {sectionEyebrow(section) && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{sectionEyebrow(section)}</p>}
            {section.title && <h2 className="mt-5 font-display text-4xl leading-tight md:text-6xl">{section.title}</h2>}
          </div>
          {section.body && <p className="max-w-2xl text-base leading-8 text-ivory/68">{section.body}</p>}
        </div>
        <div className="mt-14 grid gap-6 lg:grid-cols-3">
          {services.map((service) => (
            <article key={service.id} className={`group bg-ivory text-espresso shadow-[0_34px_90px_rgba(0,0,0,0.18)] ${service.featured ? "lg:-mt-8" : ""}`}>
              {service.image_url && (
                <div className="relative overflow-hidden">
                  <ResponsiveImage
                    src={service.image_url}
                    variants={service.image_variants}
                    alt={service.image_alt || service.title}
                    sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                    loading="lazy"
                    decoding="async"
                    className="aspect-[4/5] w-full object-cover transition duration-700 group-hover:scale-105"
                  />
                  {service.discount_label && (
                    <span className="absolute left-5 top-5 bg-espresso px-4 py-2 text-[0.68rem] font-bold uppercase tracking-[0.16em] text-champagne">
                      {service.discount_label}
                    </span>
                  )}
                </div>
              )}
              <div className="p-7">
                {service.duration && <p className="text-xs font-bold uppercase tracking-[0.2em] text-champagne">{service.duration}</p>}
                <h3 className="mt-4 font-display text-3xl leading-tight">
                  <Link href={`/glow-rituals/${service.slug}`} className="transition hover:text-champagne">
                    {service.title}
                  </Link>
                </h3>
                <p className="mt-4 text-sm leading-7 text-espresso/66">{service.short_description}</p>
                {!!service.inclusions?.length && (
                  <ul className="mt-5 grid gap-2">
                    {service.inclusions.slice(0, 4).map((item) => (
                      <li key={item} className="flex items-start gap-2 text-sm text-espresso/70">
                        <Check size={15} className="mt-1 shrink-0 text-sage" />
                        {item}
                      </li>
                    ))}
                  </ul>
                )}
                <div className="mt-7 grid gap-5 border-t border-champagne/25 pt-5">
                  <div>
                    {service.sale_price_amount && <p className="text-sm text-espresso/45 line-through">{formatPrice(service.currency, service.price_amount)}</p>}
                    {formatPrice(service.currency, service.sale_price_amount || service.price_amount) && <p className="font-display text-3xl">{formatPrice(service.currency, service.sale_price_amount || service.price_amount)}</p>}
                    {service.price_note && <p className="mt-1 text-xs uppercase tracking-[0.14em] text-espresso/52">{service.price_note}</p>}
                  </div>
                  <div className="flex items-center justify-between gap-4">
                    <RitualBookingButton service={service} className="brand-button inline-flex items-center gap-2 bg-champagne px-5 py-3 text-xs font-bold uppercase tracking-[0.14em] text-espresso transition hover:bg-espresso hover:text-ivory">
                      Book
                      <ArrowRight size={14} />
                    </RitualBookingButton>
                    <Link href={`/glow-rituals/${service.slug}`} aria-label={`View ${service.title}`} className="flex h-11 w-11 shrink-0 items-center justify-center bg-espresso text-ivory transition hover:bg-champagne hover:text-espresso">
                      <ArrowRight size={17} />
                    </Link>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function GalleryBand({ section, gallery }: { section: PageSection; gallery: GalleryImage[] }) {
  return (
    <section className="bg-cream py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="grid gap-10 md:grid-cols-[0.75fr_1.25fr]">
          <div>
            {sectionEyebrow(section) && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{sectionEyebrow(section)}</p>}
            {section.title && <h2 className="mt-5 font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>}
            {section.body && <p className="mt-6 text-base leading-8 text-espresso/68">{section.body}</p>}
            <SectionCtas section={section} />
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            {gallery.slice(0, 6).map((image, index) => (
              <figure key={image.id} className={index % 2 ? "sm:mt-12" : ""}>
                {image.image_url && (
                  <ResponsiveImage
                    src={image.image_url}
                    variants={image.image_variants}
                    alt={image.alt_text || image.title}
                    sizes="(min-width: 768px) 40vw, 100vw"
                    loading="lazy"
                    decoding="async"
                    className="aspect-[4/5] w-full object-cover shadow-[0_24px_70px_rgba(37,29,24,0.12)]"
                  />
                )}
                {image.caption && <figcaption className="px-1 py-4 text-sm leading-6 text-espresso/64">{image.caption}</figcaption>}
              </figure>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function TestimonialBand({ section, testimonials }: { section: PageSection; testimonials: Testimonial[] }) {
  if (!testimonials.length) return null;
  return (
    <section className="bg-ivory py-24 md:py-28">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="max-w-3xl">
          {sectionEyebrow(section) && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{sectionEyebrow(section)}</p>}
          {section.title && <h2 className="mt-5 font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>}
          {section.subtitle && <p className="mt-5 text-lg leading-8 text-espresso/64">{section.subtitle}</p>}
        </div>
        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {testimonials.slice(0, 3).map((item) => (
            <article key={item.id} className="border border-champagne/25 bg-white/55 p-7">
              <Quote size={30} className="text-champagne" />
              <p className="mt-6 text-base leading-8 text-espresso/72">{item.quote}</p>
              <p className="mt-7 font-display text-2xl">{item.is_anonymized ? "Client note" : item.name}</p>
              {item.role && <p className="mt-1 text-xs uppercase tracking-[0.18em] text-espresso/45">{item.role}</p>}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function FAQBand({ section, faqs }: { section: PageSection; faqs: FAQ[] }) {
  if (!faqs.length) return null;
  return (
    <section className="bg-cream py-24 md:py-28">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 md:grid-cols-[0.75fr_1.25fr] lg:px-8">
        <div>
          {sectionEyebrow(section) && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{sectionEyebrow(section)}</p>}
          {section.title && <h2 className="mt-5 font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>}
          {section.subtitle && <p className="mt-5 text-base leading-8 text-espresso/64">{section.subtitle}</p>}
        </div>
        <div className="divide-y divide-champagne/25 border-y border-champagne/25">
          {faqs.slice(0, 10).map((faq) => (
            <details key={faq.id} className="group py-5">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-6 font-display text-2xl text-espresso outline-none marker:hidden focus-visible:text-champagne">
                <span>{faq.question}</span>
                <ChevronDown size={22} className="shrink-0 text-champagne transition duration-200 group-open:rotate-180" />
              </summary>
              <p className="mt-4 max-w-3xl text-sm leading-7 text-espresso/66">{faq.answer}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}

function CtaBand({ section }: { section: PageSection }) {
  return (
    <section className="bg-espresso px-5 py-20 text-center text-ivory">
      {sectionEyebrow(section) && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{sectionEyebrow(section)}</p>}
      {section.title && <h2 className="mx-auto mt-4 max-w-4xl font-display text-4xl leading-tight md:text-6xl">{section.title}</h2>}
      {section.body && <p className="mx-auto mt-5 max-w-2xl text-base leading-8 text-ivory/68">{section.body}</p>}
      <SectionCtas section={section} tone="dark" centered />
    </section>
  );
}

function ContactBand({ section, brand }: { section: PageSection; brand?: BrandSettings }) {
  const rows = [
    brand?.contact_email ? { icon: <Mail size={18} />, value: brand.contact_email } : null,
    brand?.phone ? { icon: <Phone size={18} />, value: brand.phone } : null,
    brand?.instagram_handle ? { icon: <Instagram size={18} />, value: brand.instagram_handle } : null,
    brand?.address ? { icon: <MapPin size={18} />, value: brand.address } : null
  ].filter(Boolean) as Array<{ icon: ReactNode; value: string }>;

  return (
    <section className="bg-ivory py-20 md:py-24">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 md:grid-cols-[0.85fr_1.15fr] lg:px-8">
        <div>
          {sectionEyebrow(section) && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{sectionEyebrow(section)}</p>}
          {section.title && <h2 className="mt-5 font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>}
          {section.body && <p className="mt-6 text-base leading-8 text-espresso/68">{section.body}</p>}
        </div>
        {!!rows.length && (
          <div className="border border-champagne/25 bg-cream p-7 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
            <div className="grid gap-5 text-espresso/74">
              {rows.map((row) => (
                <div key={row.value} className="flex gap-3 text-sm leading-7">
                  <span className="mt-1 text-champagne">{row.icon}</span>
                  <span>{row.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function SectionCtas({ section, tone, centered }: { section: PageSection; tone?: "dark"; centered?: boolean }) {
  const wrapperClass = `mt-8 flex flex-wrap items-center gap-4 ${centered ? "justify-center" : ""}`;
  const primary = section.cta_label && section.cta_url ? { label: section.cta_label, url: section.cta_url, style: section.cta_style } : null;
  const secondary = section.secondary_cta_label && section.secondary_cta_url ? { label: section.secondary_cta_label, url: section.secondary_cta_url, style: section.secondary_cta_style } : null;
  if (!primary && !secondary) return null;
  return (
    <div className={wrapperClass}>
      {primary && (
        <Link href={primary.url} className={ctaClass(primary.style, tone)}>
          {primary.label}
          <ArrowRight size={15} />
        </Link>
      )}
      {secondary && (
        <Link href={secondary.url} className={ctaClass(secondary.style || "secondary", tone)}>
          {secondary.label}
          <ArrowRight size={15} />
        </Link>
      )}
    </div>
  );
}

function ctaClass(style: string | undefined, tone?: "dark") {
  if (style === "secondary") {
    return `brand-button inline-flex items-center gap-3 border-b border-champagne pb-2 text-sm font-bold uppercase tracking-[0.16em] ${tone === "dark" ? "text-ivory hover:text-champagne" : "text-espresso hover:text-champagne"}`;
  }
  if (style === "dark") {
    return "brand-button inline-flex items-center gap-3 bg-espresso px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-ivory transition hover:bg-champagne hover:text-espresso";
  }
  return "brand-button inline-flex items-center gap-3 bg-champagne px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-espresso transition hover:bg-espresso hover:text-ivory";
}

function sectionEyebrow(section: PageSection) {
  return section.eyebrow;
}

function formatPrice(currency: string, value: string | null) {
  if (!value) return "";
  const amount = Number(value);
  if (!Number.isFinite(amount)) return value;
  if (currency === "INR") return `₹${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  return `${currency} ${amount.toLocaleString()}`;
}
