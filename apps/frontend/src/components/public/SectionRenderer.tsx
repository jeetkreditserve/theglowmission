import Link from "next/link";
import type { GalleryImage, PageSection, Service } from "@/types/cms";

export function SectionRenderer({ sections, services, gallery }: { sections: PageSection[]; services: Service[]; gallery: GalleryImage[] }) {
  return (
    <>
      {sections
        .filter((section) => section.section_type !== "hero")
        .map((section, index) => {
          if (section.section_type === "services") {
            return <ServiceBand key={section.id} section={section} services={services} />;
          }
          if (section.section_type === "gallery") {
            return <GalleryBand key={section.id} section={section} gallery={gallery} />;
          }
          return <StoryBand key={section.id} section={section} flip={index % 2 === 1} />;
        })}
    </>
  );
}

function StoryBand({ section, flip }: { section: PageSection; flip?: boolean }) {
  return (
    <section className="bg-ivory py-20">
      <div className={`mx-auto grid max-w-7xl items-center gap-12 px-5 md:grid-cols-2 lg:px-8 ${flip ? "md:[&>*:first-child]:order-2" : ""}`}>
        <div>
          <p className="display-title text-sm text-champagne">{section.subtitle || "The Glow Mission"}</p>
          <h2 className="mt-4 font-display text-4xl leading-tight text-espresso md:text-5xl">{section.title}</h2>
          <p className="mt-6 text-base leading-8 text-espresso/68">{section.body}</p>
          {section.cta_label && (
            <Link href={section.cta_url || "/about"} className="mt-8 inline-block border-b border-champagne pb-2 text-sm font-semibold uppercase tracking-[0.18em]">
              {section.cta_label}
            </Link>
          )}
        </div>
        <div className="border border-champagne/30 bg-cream p-6">
          <img src="/reference/glow-mission-logo-3d.png" alt="" className="aspect-square w-full object-cover" />
        </div>
      </div>
    </section>
  );
}

function ServiceBand({ section, services }: { section: PageSection; services: Service[] }) {
  return (
    <section className="bg-cream py-20">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="max-w-3xl">
          <p className="display-title text-sm text-champagne">{section.subtitle}</p>
          <h2 className="mt-4 font-display text-4xl leading-tight text-espresso md:text-5xl">{section.title}</h2>
          <p className="mt-5 text-base leading-8 text-espresso/68">{section.body}</p>
        </div>
        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {services.map((service) => (
            <article key={service.id} className="border border-champagne/30 bg-ivory p-7">
              <p className="display-title text-xs text-champagne">{service.duration}</p>
              <h3 className="mt-5 font-display text-2xl text-espresso">{service.title}</h3>
              <p className="mt-4 text-sm leading-7 text-espresso/66">{service.short_description}</p>
              <p className="mt-6 text-xs font-semibold uppercase tracking-[0.18em] text-espresso/55">{service.price_note}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function GalleryBand({ section, gallery }: { section: PageSection; gallery: GalleryImage[] }) {
  return (
    <section className="bg-ivory py-20">
      <div className="mx-auto max-w-7xl px-5 lg:px-8">
        <div className="grid gap-10 md:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="display-title text-sm text-champagne">{section.subtitle}</p>
            <h2 className="mt-4 font-display text-4xl leading-tight text-espresso md:text-5xl">{section.title}</h2>
            <p className="mt-5 text-base leading-8 text-espresso/68">{section.body}</p>
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            {(gallery.length ? gallery : [{ id: 1, title: "Glow", alt_text: "", image_url: "/reference/glow-mission-post-1.png", caption: "Skin that glows.", active: true, ordering: 0 }]).map(
              (image) => (
                <figure key={image.id} className="border border-champagne/25 bg-cream p-3">
                  <img src={image.image_url || "/reference/glow-mission-post-1.png"} alt={image.alt_text || image.title} className="aspect-[4/5] w-full object-cover" />
                  <figcaption className="px-2 py-4 text-sm text-espresso/64">{image.caption}</figcaption>
                </figure>
              )
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

