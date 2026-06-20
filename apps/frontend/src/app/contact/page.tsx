import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowRight, Instagram, Mail, MapPin, Phone } from "lucide-react";
import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, getBrandSettings } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ContactPage() {
  const brand = await getBrandSettings().catch(() => fallbackBrand());

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="bg-ivory">
        <section className="mx-auto grid min-h-[76vh] max-w-7xl items-center gap-12 px-5 py-24 md:grid-cols-[0.95fr_1.05fr] lg:px-8">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">Contact</p>
            <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">Begin with the ritual your skin is asking for.</h1>
            <p className="mt-7 text-lg leading-9 text-espresso/70">Tell us what you want to feel: rested, lifted, brighter, softer, or simply cared for. We will guide you into the right session.</p>
            <Link href="/campaigns/glow-consultation" className="mt-9 inline-flex items-center gap-3 bg-espresso px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-ivory transition hover:bg-champagne hover:text-espresso">
              Book a consultation
              <ArrowRight size={16} />
            </Link>
          </div>
          <div className="border border-champagne/25 bg-cream p-8 shadow-[0_24px_80px_rgba(37,29,24,0.08)]">
            <img src="/generated/glow-hero-offer.png" alt="Luxury spa consultation setup" className="aspect-[16/9] w-full object-cover" />
            <div className="mt-8 grid gap-5 text-espresso/74">
              <ContactLine icon={<Mail size={18} />} text={brand.contact_email || "hello@theglowmission.com"} />
              <ContactLine icon={<Phone size={18} />} text={brand.phone || "Phone number can be added in CMS"} />
              <ContactLine icon={<Instagram size={18} />} text={brand.instagram_handle || "@theglowmission"} />
              <ContactLine icon={<MapPin size={18} />} text={brand.address || brand.essence} />
            </div>
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}

function ContactLine({ icon, text }: { icon: ReactNode; text: string }) {
  return (
    <div className="flex gap-3 text-sm leading-7">
      <span className="mt-1 text-champagne">{icon}</span>
      <span>{text}</span>
    </div>
  );
}
