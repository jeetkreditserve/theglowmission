import Link from "next/link";
import { ArrowRight, Check, Quote } from "lucide-react";
import type { FAQ, GalleryImage, PageSection, Service, Testimonial } from "@/types/cms";

export function SectionRenderer({
  sections,
  services,
  gallery,
  faqs,
  testimonials
}: {
  sections: PageSection[];
  services: Service[];
  gallery: GalleryImage[];
  faqs: FAQ[];
  testimonials: Testimonial[];
}) {
  const visible = sections.filter((section) => section.section_type !== "hero");

  return (
    <>
      {visible.map((section, index) => {
        if (section.section_type === "services") return <ServiceBand key={section.id} section={section} services={services} />;
        if (section.section_type === "gallery") return <GalleryBand key={section.id} section={section} gallery={gallery} />;
        if (section.section_type === "testimonials") return <TestimonialBand key={section.id} section={section} testimonials={testimonials} />;
        if (section.section_type === "faqs") return <FAQBand key={section.id} section={section} faqs={faqs} />;
        if (section.section_type === "cta") return <CtaBand key={section.id} section={section} />;
        return <StoryBand key={section.id} section={section} flip={index % 2 === 1} />;
      })}
      {!!testimonials.length && !visible.some((section) => section.section_type === "testimonials") && (
        <TestimonialBand testimonials={testimonials} section={{ id: 0, section_type: "testimonials", title: "What clients notice first", subtitle: "Softness, calm, and visible rest.", body: "", media_url: null, cta_label: "", cta_url: "", ordering: 0, active: true, config: {} }} />
      )}
      {!!faqs.length && !visible.some((section) => section.section_type === "faqs") && (
        <FAQBand faqs={faqs} section={{ id: 0, section_type: "faqs", title: "Questions before you book", subtitle: "Clear, calm answers for your first visit.", body: "", media_url: null, cta_label: "", cta_url: "", ordering: 0, active: true, config: {} }} />
      )}
    </>
  );
}

function StoryBand({ section, flip }: { section: PageSection; flip?: boolean }) {
  const image = section.media_url || "/generated/glow-about-story.png";
  return (
    <section className="bg-ivory py-24 md:py-32">
      <div className={`mx-auto grid max-w-7xl items-center gap-14 px-5 md:grid-cols-[0.95fr_1.05fr] lg:px-8 ${flip ? "md:[&>*:first-child]:order-2" : ""}`}>
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{section.subtitle || "The Glow Mission"}</p>
          <h2 className="mt-5 max-w-2xl font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>
          <p className="mt-7 max-w-2xl text-base leading-8 text-espresso/68">{section.body}</p>
          {section.cta_label && (
            <Link href={section.cta_url || "/about"} className="mt-8 inline-flex items-center gap-3 border-b border-champagne pb-2 text-sm font-bold uppercase tracking-[0.16em] text-espresso">
              {section.cta_label}
              <ArrowRight size={15} />
            </Link>
          )}
        </div>
        <figure className="relative">
          <div className="absolute -left-5 -top-5 h-full w-full border border-champagne/35" />
          <img src={image} alt={section.title} className="relative aspect-[4/5] w-full object-cover shadow-[0_34px_90px_rgba(37,29,24,0.18)]" />
        </figure>
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
            <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{section.subtitle}</p>
            <h2 className="mt-5 font-display text-4xl leading-tight md:text-6xl">{section.title}</h2>
          </div>
          <p className="max-w-2xl text-base leading-8 text-ivory/68">{section.body}</p>
        </div>
        <div className="mt-14 grid gap-6 lg:grid-cols-3">
          {services.map((service) => (
            <article key={service.id} className={`group bg-ivory text-espresso shadow-[0_34px_90px_rgba(0,0,0,0.18)] ${service.featured ? "lg:-mt-8" : ""}`}>
              <div className="relative overflow-hidden">
                <img src={service.image_url || serviceFallback(service)} alt={service.image_alt || service.title} className="aspect-[4/5] w-full object-cover transition duration-700 group-hover:scale-105" />
                {(service.discount_label || service.featured) && (
                  <span className="absolute left-5 top-5 bg-espresso px-4 py-2 text-[0.68rem] font-bold uppercase tracking-[0.16em] text-champagne">
                    {service.discount_label || "Featured"}
                  </span>
                )}
              </div>
              <div className="p-7">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-champagne">{service.duration}</p>
                <h3 className="mt-4 font-display text-3xl leading-tight">{service.title}</h3>
                <p className="mt-4 text-sm leading-7 text-espresso/66">{service.short_description}</p>
                <ul className="mt-5 grid gap-2">
                  {service.inclusions?.slice(0, 4).map((item) => (
                    <li key={item} className="flex items-start gap-2 text-sm text-espresso/70">
                      <Check size={15} className="mt-1 shrink-0 text-sage" />
                      {item}
                    </li>
                  ))}
                </ul>
                <div className="mt-7 flex items-end justify-between gap-4 border-t border-champagne/25 pt-5">
                  <div>
                    {service.sale_price_amount && <p className="text-sm text-espresso/45 line-through">{formatPrice(service.currency, service.price_amount)}</p>}
                    <p className="font-display text-3xl">{formatPrice(service.currency, service.sale_price_amount || service.price_amount)}</p>
                    <p className="mt-1 text-xs uppercase tracking-[0.14em] text-espresso/52">{service.price_note}</p>
                  </div>
                  <Link href={service.cta_url || "/campaigns/glow-consultation"} className="flex h-11 w-11 shrink-0 items-center justify-center bg-champagne text-espresso transition hover:bg-espresso hover:text-ivory">
                    <ArrowRight size={17} />
                  </Link>
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
  const images = gallery.length
    ? gallery
    : [
        { id: 1, title: "Glow", alt_text: "Luxury facial ritual", image_url: "/generated/glow-service-signature.png", caption: "Skin that glows. Confidence that shows.", active: true, ordering: 0 },
        { id: 2, title: "Botanicals", alt_text: "Natural facial ingredients", image_url: "/generated/glow-service-natural-facial.png", caption: "Botanical textures and warm natural care.", active: true, ordering: 1 }
      ];
  return (
    <section className="bg-cream py-24 md:py-32">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="grid gap-10 md:grid-cols-[0.75fr_1.25fr]">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{section.subtitle}</p>
            <h2 className="mt-5 font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>
            <p className="mt-6 text-base leading-8 text-espresso/68">{section.body}</p>
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            {images.slice(0, 4).map((image, index) => (
              <figure key={image.id} className={index % 2 ? "sm:mt-12" : ""}>
                <img src={image.image_url || "/generated/glow-service-signature.png"} alt={image.alt_text || image.title} className="aspect-[4/5] w-full object-cover shadow-[0_24px_70px_rgba(37,29,24,0.12)]" />
                <figcaption className="px-1 py-4 text-sm leading-6 text-espresso/64">{image.caption}</figcaption>
              </figure>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function TestimonialBand({ section, testimonials }: { section: PageSection; testimonials: Testimonial[] }) {
  return (
    <section className="bg-ivory py-24 md:py-28">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="max-w-3xl">
          <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{section.subtitle}</p>
          <h2 className="mt-5 font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>
        </div>
        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {testimonials.slice(0, 3).map((item) => (
            <article key={item.id} className="border border-champagne/25 bg-white/55 p-7">
              <Quote size={30} className="text-champagne" />
              <p className="mt-6 text-base leading-8 text-espresso/72">{item.quote}</p>
              <p className="mt-7 font-display text-2xl">{item.name}</p>
              <p className="mt-1 text-xs uppercase tracking-[0.18em] text-espresso/45">{item.role}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function FAQBand({ section, faqs }: { section: PageSection; faqs: FAQ[] }) {
  return (
    <section className="bg-cream py-24 md:py-28">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 md:grid-cols-[0.75fr_1.25fr] lg:px-8">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{section.subtitle}</p>
          <h2 className="mt-5 font-display text-4xl leading-tight text-espresso md:text-6xl">{section.title}</h2>
        </div>
        <div className="divide-y divide-champagne/25 border-y border-champagne/25">
          {faqs.slice(0, 8).map((faq) => (
            <details key={faq.id} className="group py-5">
              <summary className="cursor-pointer list-none font-display text-2xl text-espresso marker:hidden">{faq.question}</summary>
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
      <h2 className="mx-auto max-w-4xl font-display text-4xl leading-tight md:text-6xl">{section.title}</h2>
      <p className="mx-auto mt-5 max-w-2xl text-base leading-8 text-ivory/68">{section.body}</p>
      {section.cta_label && (
        <Link href={section.cta_url || "/campaigns/glow-consultation"} className="mt-9 inline-flex items-center gap-3 bg-champagne px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-espresso">
          {section.cta_label}
          <ArrowRight size={16} />
        </Link>
      )}
    </section>
  );
}

function serviceFallback(service: Service) {
  if (service.slug.includes("face-yoga")) return "/generated/glow-service-face-yoga.png";
  if (service.slug.includes("natural")) return "/generated/glow-service-natural-facial.png";
  return "/generated/glow-service-signature.png";
}

function formatPrice(currency: string, value: string | null) {
  if (!value) return "Price on request";
  const amount = Number(value);
  if (!Number.isFinite(amount)) return value;
  if (currency === "INR") return `₹${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  return `${currency} ${amount.toLocaleString()}`;
}
