import Link from "next/link";
import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, fallbackServices, getBrandSettings, getServices } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function GlowRitualsPage() {
  const [brand, services] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getServices().catch(() => fallbackServices)]);

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="texture-bg">
        <section className="mx-auto max-w-7xl px-5 py-20 lg:px-8">
          <div className="grid gap-12 md:grid-cols-[0.95fr_1.05fr]">
            <div>
              <p className="display-title text-sm text-champagne">Ritual menu</p>
              <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">Skin that glows. Confidence that shows.</h1>
              <p className="mt-7 text-lg leading-9 text-espresso/70">
                Choose the ritual that matches the way your skin and face want to feel: rested, lifted, brighter, softer, or simply cared for.
              </p>
              <Link href="/campaigns/glow-consultation" className="mt-9 inline-block bg-champagne px-7 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-white">
                Book a Glow Ritual
              </Link>
            </div>
            <div className="space-y-5">
              {services.map((service, index) => (
                <article key={service.id} className="border border-champagne/30 bg-white/45 p-7">
                  <p className="display-title text-xs text-champagne">0{index + 1}</p>
                  <h2 className="mt-3 font-display text-3xl text-espresso">{service.title}</h2>
                  <p className="mt-3 text-sm leading-7 text-espresso/68">{service.short_description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
