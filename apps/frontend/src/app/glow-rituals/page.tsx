import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Footer } from "@/components/public/Footer";
import { BrandTheme } from "@/components/public/BrandTheme";
import { PublicHeader } from "@/components/public/PublicHeader";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";
import { fallbackBrand, fallbackServices, getBrandSettings, getServices } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function GlowRitualsPage() {
  const [brand, services] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getServices().catch(() => fallbackServices)]);

  return (
    <BrandTheme brand={brand}>
      <PublicHeader brand={brand} />
      <main className="bg-cream">
        <section className="mx-auto grid max-w-7xl gap-12 px-5 py-24 md:grid-cols-[0.9fr_1.1fr] lg:px-8">
          <div className="md:sticky md:top-28 md:self-start">
            <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">Ritual menu</p>
            <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">Choose the way you want to feel after one quiet hour.</h1>
            <p className="mt-7 text-lg leading-9 text-espresso/68">
              Rested, lifted, brighter, softer, or simply cared for. Each ritual can be updated in the CMS as new treatments and offers launch.
            </p>
            <Link href="/campaigns/glow-consultation" className="brand-button mt-9 inline-flex items-center gap-3 bg-espresso px-7 py-4 text-sm font-bold text-ivory transition hover:bg-champagne hover:text-espresso">
              Book a consultation
              <ArrowRight size={16} />
            </Link>
          </div>
          <div className="space-y-5">
            {services.map((service, index) => (
              <article key={service.id} className="grid gap-5 border border-champagne/25 bg-ivory p-5 shadow-[0_18px_50px_rgba(37,29,24,0.08)] sm:grid-cols-[180px_1fr]">
                <ResponsiveImage
                  src={service.image_url || fallbackImage(index)}
                  variants={service.image_variants}
                  fallbackSrc={fallbackImage(index)}
                  alt={service.image_alt || service.title}
                  sizes="(min-width: 640px) 180px, 100vw"
                  loading={index === 0 ? "eager" : "lazy"}
                  fetchPriority={index === 0 ? "high" : "auto"}
                  decoding="async"
                  className="aspect-[4/5] w-full object-cover"
                />
                <div className="py-1">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-champagne">0{index + 1} / {service.duration}</p>
                  <h2 className="mt-3 font-display text-3xl text-espresso">{service.title}</h2>
                  <p className="mt-3 text-sm leading-7 text-espresso/66">{service.short_description}</p>
                  <p className="mt-5 text-sm font-bold text-espresso">{service.sale_price_amount || service.price_amount ? `${service.currency === "INR" ? "₹" : service.currency} ${Number(service.sale_price_amount || service.price_amount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}` : "Price on request"}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </BrandTheme>
  );
}

function fallbackImage(index: number) {
  if (index === 1) return "/generated/glow-service-face-yoga.webp";
  if (index === 2) return "/generated/glow-service-natural-facial.webp";
  return "/generated/glow-service-signature.webp";
}
