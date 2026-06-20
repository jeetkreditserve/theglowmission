import Link from "next/link";
import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, getBrandSettings } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ContactPage() {
  const brand = await getBrandSettings().catch(() => fallbackBrand());

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="texture-bg">
        <section className="mx-auto grid min-h-[70vh] max-w-7xl items-center gap-12 px-5 py-20 md:grid-cols-2 lg:px-8">
          <div>
            <p className="display-title text-sm text-champagne">Contact</p>
            <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">Begin your glow ritual.</h1>
            <p className="mt-7 text-lg leading-9 text-espresso/70">Tell us what your skin is asking for and we will guide you into the right ritual.</p>
            <Link href="/campaigns/glow-consultation" className="mt-9 inline-block bg-champagne px-7 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-white">
              Book a Glow Ritual
            </Link>
          </div>
          <div className="border border-champagne/30 bg-cream p-8">
            <p className="display-title text-sm text-champagne">The Glow Mission</p>
            <p className="mt-6 text-lg text-espresso">{brand.contact_email}</p>
            <p className="mt-3 text-lg text-espresso">{brand.phone}</p>
            <p className="mt-3 text-lg text-espresso">{brand.instagram_handle}</p>
            <p className="mt-8 text-sm leading-7 text-espresso/65">{brand.address || brand.essence}</p>
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
