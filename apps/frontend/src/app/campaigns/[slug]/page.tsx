import { notFound } from "next/navigation";
import { CampaignFormClient } from "@/components/public/CampaignFormClient";
import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, getBrandSettings, getCampaignForm } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function CampaignPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [brand, form] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getCampaignForm(slug).catch(() => null)]);
  if (!form) {
    notFound();
  }

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="bg-espresso text-ivory">
        <section className="mx-auto grid min-h-[calc(100vh-78px)] max-w-7xl gap-12 px-5 py-20 md:grid-cols-[0.9fr_1.1fr] md:items-center lg:px-8">
          <div>
            {form.offer_label && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{form.offer_label}</p>}
            <h1 className="mt-5 font-display text-5xl leading-tight text-ivory md:text-7xl">{form.title}</h1>
            <p className="mt-7 text-lg leading-9 text-ivory/70">
              {form.summary || "Share a few details about your skin, your schedule, and the kind of glow ritual you are looking for."}
            </p>
            <img
              src={form.hero_image_url || "/generated/glow-hero-offer.png"}
              alt={form.hero_image_alt || form.title}
              className="mt-10 aspect-[16/9] w-full object-cover shadow-[0_34px_90px_rgba(0,0,0,0.24)]"
            />
          </div>
          <div className="border border-champagne/25 bg-ivory p-6 text-espresso shadow-[0_34px_90px_rgba(0,0,0,0.22)] md:p-9">
            <CampaignFormClient form={form} />
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
