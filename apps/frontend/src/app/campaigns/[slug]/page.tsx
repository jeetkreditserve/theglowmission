import { notFound } from "next/navigation";
import { CampaignFormClient } from "@/components/public/CampaignFormClient";
import { Footer } from "@/components/public/Footer";
import { BrandTheme } from "@/components/public/BrandTheme";
import { PublicHeader } from "@/components/public/PublicHeader";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";
import { fallbackBrand, getBrandSettings, getCampaignForm, getNavigationItems } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const form = await getCampaignForm(slug).catch(() => null);
  if (!form) return {};
  return {
    title: form.seo_title || form.title,
    description: form.seo_description || form.summary || undefined
  };
}

export default async function CampaignPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [brand, navigationItems, form] = await Promise.all([
    getBrandSettings().catch(() => fallbackBrand()),
    getNavigationItems().catch(() => []),
    getCampaignForm(slug).catch(() => null)
  ]);
  if (!form) {
    notFound();
  }

  return (
    <BrandTheme brand={brand}>
      <PublicHeader brand={brand} navigationItems={navigationItems} />
      <main className="bg-espresso text-ivory">
        <section className="mx-auto grid min-h-[calc(100vh-78px)] max-w-7xl gap-12 px-5 py-20 md:grid-cols-[0.9fr_1.1fr] md:items-center lg:px-8">
          <div>
            {form.offer_label && <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{form.offer_label}</p>}
            <h1 className="mt-5 font-display text-5xl leading-tight text-ivory md:text-7xl">{form.title}</h1>
            {form.summary && <p className="mt-7 text-lg leading-9 text-ivory/70">{form.summary}</p>}
            {form.hero_image_url && (
              <ResponsiveImage
                src={form.hero_image_url}
                variants={form.hero_image_variants}
                alt={form.hero_image_alt || form.title}
                sizes="(min-width: 768px) 45vw, 100vw"
                loading="eager"
                fetchPriority="high"
                decoding="async"
                className="mt-10 aspect-[16/9] w-full object-cover shadow-[0_34px_90px_rgba(0,0,0,0.24)]"
              />
            )}
          </div>
          <div className="border border-champagne/25 bg-ivory p-6 text-espresso shadow-[0_34px_90px_rgba(0,0,0,0.22)] md:p-9">
            <CampaignFormClient form={form} />
          </div>
        </section>
      </main>
      <Footer brand={brand} navigationItems={navigationItems} />
    </BrandTheme>
  );
}
