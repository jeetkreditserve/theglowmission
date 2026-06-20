import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, fallbackServices, getBrandSettings, getServices } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ServicesPage() {
  const [brand, services] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getServices().catch(() => fallbackServices)]);

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="bg-ivory">
        <section className="mx-auto max-w-7xl px-5 py-20 lg:px-8">
          <div className="max-w-3xl">
            <p className="display-title text-sm text-champagne">Glow rituals</p>
            <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">One peaceful hour of care.</h1>
            <p className="mt-7 text-lg leading-9 text-espresso/70">
              Natural ingredients, face yoga, facial massage, lifting techniques, and calming rituals come together for skin that feels rested and visibly cared for.
            </p>
          </div>
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {services.map((service) => (
              <article key={service.id} className="border border-champagne/30 bg-cream p-8">
                <p className="display-title text-sm text-champagne">{service.duration}</p>
                <h2 className="mt-5 font-display text-3xl text-espresso">{service.title}</h2>
                <p className="mt-5 text-sm leading-7 text-espresso/68">{service.description || service.short_description}</p>
                <p className="mt-8 text-xs font-semibold uppercase tracking-[0.18em] text-espresso/60">{service.price_note}</p>
              </article>
            ))}
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
