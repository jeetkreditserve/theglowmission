import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, getBrandSettings, getPage } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function AboutPage() {
  const [brand, page] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getPage("about").catch(() => null)]);
  const body = page?.sections[0]?.body || brand.mission_statement;

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="bg-ivory">
        <section className="mx-auto grid min-h-[78vh] max-w-7xl items-center gap-14 px-5 py-24 md:grid-cols-[0.9fr_1.1fr] lg:px-8">
          <figure className="relative">
            <div className="absolute -left-5 -top-5 h-full w-full border border-champagne/35" />
            <img src="/generated/glow-about-story.png" alt="Founder-led natural facial care story" className="relative aspect-[4/5] w-full object-cover shadow-[0_34px_90px_rgba(37,29,24,0.16)]" />
          </figure>
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">A mission of care</p>
            <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">A boutique ritual shaped by natural care and patient hands.</h1>
            <p className="mt-7 text-lg leading-9 text-espresso/70">{body}</p>
            <Link href="/campaigns/glow-consultation" className="mt-9 inline-flex items-center gap-3 bg-espresso px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-ivory transition hover:bg-champagne hover:text-espresso">
              Start with a consultation
              <ArrowRight size={16} />
            </Link>
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
