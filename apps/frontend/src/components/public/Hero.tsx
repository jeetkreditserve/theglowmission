import Link from "next/link";
import type { BrandSettings, PageSection, Service } from "@/types/cms";

export function Hero({ brand, section, services }: { brand: BrandSettings; section?: PageSection; services: Service[] }) {
  return (
    <section className="texture-bg relative overflow-hidden">
      <div className="mx-auto grid min-h-[68vh] max-w-7xl items-center gap-8 px-5 py-8 md:min-h-[72vh] md:grid-cols-[1fr_0.92fr] md:py-10 lg:px-8">
        <div className="relative z-10 max-w-3xl">
          <div className="gold-rule mb-7 w-64" />
          <h1 className="font-display text-5xl leading-[1.06] text-espresso md:text-7xl lg:text-8xl">
            {section?.title || brand.tagline}
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-espresso/74 md:text-xl">{section?.subtitle || brand.essence}</p>
          <p className="mt-4 max-w-xl text-base leading-7 text-espresso/62">{section?.body || "Skin that glows. Confidence that shows."}</p>
          <div className="mt-8 flex flex-wrap items-center gap-5">
            <Link
              href={section?.cta_url || "/campaigns/glow-consultation"}
              className="bg-champagne px-7 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-espresso"
            >
              {section?.cta_label || "Book a Glow Ritual"}
            </Link>
            <Link href="/services" className="text-sm font-semibold uppercase tracking-[0.18em] text-espresso underline decoration-champagne/70 underline-offset-8">
              Explore services
            </Link>
          </div>
        </div>
        <div className="relative">
          <div className="absolute -right-20 -top-16 h-60 w-60 rounded-full bg-champagne/20 blur-3xl" />
          <img
            src="/reference/glow-mission-post-1.png"
            alt="The Glow Mission natural glow skincare composition"
            className="spa-shadow relative z-10 aspect-square w-full border border-white/70 object-cover"
          />
        </div>
      </div>
      <div className="mx-auto max-w-7xl px-5 pb-12 lg:px-8">
        <div className="grid border-y border-champagne/30 bg-white/34 md:grid-cols-3">
          {services.slice(0, 3).map((service) => (
            <Link key={service.id} href="/services" className="border-champagne/25 p-6 transition hover:bg-white/40 md:border-r md:last:border-r-0">
              <p className="display-title text-sm text-champagne">{service.duration}</p>
              <h2 className="mt-3 font-display text-2xl text-espresso">{service.title}</h2>
              <p className="mt-3 text-sm leading-6 text-espresso/65">{service.short_description}</p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
