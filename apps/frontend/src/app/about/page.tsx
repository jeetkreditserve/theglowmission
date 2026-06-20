import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, getBrandSettings, getPage } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function AboutPage() {
  const [brand, page] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getPage("about").catch(() => null)]);
  const body =
    page?.sections[0]?.body ||
    "The Glow Mission carries forward a mother's wisdom in cosmetology, natural ingredients, massage, consistency, and gentle hands.";

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="texture-bg">
        <section className="mx-auto grid min-h-[72vh] max-w-7xl items-center gap-12 px-5 py-20 md:grid-cols-[0.9fr_1.1fr] lg:px-8">
          <div className="border border-champagne/30 bg-cream p-5">
            <img src="/reference/glow-mission-logo-3d.png" alt={brand.site_title} className="aspect-square w-full object-cover" />
          </div>
          <div>
            <p className="display-title text-sm text-champagne">A mission of care</p>
            <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">A legacy carried forward.</h1>
            <p className="mt-7 text-lg leading-9 text-espresso/70">{body}</p>
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
