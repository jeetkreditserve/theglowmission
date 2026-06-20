import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";
import { Footer } from "@/components/public/Footer";
import { BrandTheme } from "@/components/public/BrandTheme";
import { PublicHeader } from "@/components/public/PublicHeader";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";
import { fallbackBrand, fallbackServices, getBrandSettings, getServices } from "@/lib/api";
import type { Service } from "@/types/cms";

export const dynamic = "force-dynamic";

export default async function ServicesPage() {
  const [brand, services] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getServices().catch(() => fallbackServices)]);

  return (
    <BrandTheme brand={brand}>
      <PublicHeader brand={brand} />
      <main className="bg-ivory">
        <section className="relative overflow-hidden bg-espresso px-5 py-24 text-ivory md:py-32 lg:px-8">
          <ResponsiveImage
            src="/generated/glow-hero-signature.webp"
            fallbackSrc="/generated/glow-hero-signature.webp"
            alt=""
            sizes="100vw"
            loading="eager"
            fetchPriority="high"
            decoding="async"
            className="absolute inset-0 h-full w-full object-cover opacity-[0.34]"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-espresso via-espresso/80 to-espresso/28" />
          <div className="relative mx-auto max-w-7xl">
            <h1 className="max-w-4xl font-display text-5xl leading-[1] md:text-7xl">Treatment rituals for glow, lift, and deep facial rest.</h1>
            <p className="mt-7 max-w-2xl text-lg leading-9 text-ivory/72">
              Edit every treatment, price, discount, image, and booking link from the CMS as your menu grows.
            </p>
          </div>
        </section>
        <section className="mx-auto max-w-7xl px-5 py-20 lg:px-8">
          <div className="grid gap-8">
            {services.map((service, index) => (
              <ServiceRow key={service.id} service={service} flip={index % 2 === 1} />
            ))}
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </BrandTheme>
  );
}

function ServiceRow({ service, flip }: { service: Service; flip?: boolean }) {
  return (
    <article className={`grid overflow-hidden border border-champagne/25 bg-cream shadow-[0_24px_80px_rgba(37,29,24,0.08)] md:grid-cols-2 ${flip ? "md:[&>*:first-child]:order-2" : ""}`}>
      <ResponsiveImage
        src={service.image_url || fallbackImage(service)}
        variants={service.image_variants}
        fallbackSrc={fallbackImage(service)}
        alt={service.image_alt || service.title}
        sizes="(min-width: 768px) 50vw, 100vw"
        loading="lazy"
        decoding="async"
        className="h-full min-h-[420px] w-full object-cover"
      />
      <div className="flex flex-col justify-center p-7 md:p-10">
        <p className="text-xs font-bold uppercase tracking-[0.22em] text-champagne">{service.duration}</p>
        <h2 className="mt-4 font-display text-4xl leading-tight text-espresso md:text-5xl">{service.title}</h2>
        <p className="mt-5 text-base leading-8 text-espresso/68">{service.description || service.short_description}</p>
        <ul className="mt-7 grid gap-2">
          {service.inclusions?.map((item) => (
            <li key={item} className="flex gap-3 text-sm text-espresso/70">
              <Check size={16} className="mt-1 shrink-0 text-sage" />
              {item}
            </li>
          ))}
        </ul>
        <div className="mt-8 flex flex-wrap items-end justify-between gap-5 border-t border-champagne/25 pt-6">
          <div>
            {service.discount_label && <p className="text-xs font-bold uppercase tracking-[0.16em] text-sage">{service.discount_label}</p>}
            <p className="mt-2 font-display text-4xl">{formatPrice(service.currency, service.sale_price_amount || service.price_amount)}</p>
            {service.sale_price_amount && <p className="text-sm text-espresso/44 line-through">{formatPrice(service.currency, service.price_amount)}</p>}
            <p className="mt-2 text-xs uppercase tracking-[0.14em] text-espresso/50">{service.price_note}</p>
          </div>
          <Link href={service.cta_url || "/campaigns/glow-consultation"} className="brand-button inline-flex items-center gap-3 bg-espresso px-6 py-4 text-xs font-bold text-ivory transition hover:bg-champagne hover:text-espresso">
            {service.cta_label || "Book this ritual"}
            <ArrowRight size={15} />
          </Link>
        </div>
      </div>
    </article>
  );
}

function fallbackImage(service: Service) {
  if (service.slug.includes("face-yoga")) return "/generated/glow-service-face-yoga.webp";
  if (service.slug.includes("natural")) return "/generated/glow-service-natural-facial.webp";
  return "/generated/glow-service-signature.webp";
}

function formatPrice(currency: string, value: string | null) {
  if (!value) return "Price on request";
  const amount = Number(value);
  if (!Number.isFinite(amount)) return value;
  if (currency === "INR") return `₹${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  return `${currency} ${amount.toLocaleString()}`;
}
