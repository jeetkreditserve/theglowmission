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
      <main className="texture-bg">
        <section className="mx-auto grid max-w-7xl gap-12 px-5 py-20 md:grid-cols-[0.95fr_1.05fr] lg:px-8">
          <div>
            <p className="display-title text-sm text-champagne">The Glow Mission</p>
            <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">{form.title}</h1>
            <p className="mt-7 text-lg leading-9 text-espresso/70">
              Share a few details about your skin, your schedule, and the kind of glow ritual you are looking for.
            </p>
          </div>
          <div className="border border-champagne/30 bg-cream p-6 md:p-9">
            <CampaignFormClient form={form} />
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
