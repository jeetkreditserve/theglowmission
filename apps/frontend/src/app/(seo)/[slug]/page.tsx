import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { BrandTheme } from "@/components/public/BrandTheme";
import { Footer } from "@/components/public/Footer";
import { JsonLd } from "@/components/public/JsonLd";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, getBrandSettings, getNavigationItems } from "@/lib/api";
import { pageMetadata } from "@/lib/metadata";
import { getSeoPage, seoPageMap } from "@/lib/seo-content";
import { breadcrumbJsonLd, localBusinessJsonLd, organizationJsonLd, webPageJsonLd, websiteJsonLd } from "@/lib/structured-data";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const page = getSeoPage(slug);
  if (!page) return {};
  return pageMetadata({
    title: page.title,
    description: page.description,
    path: `/${page.slug}`
  });
}

export default async function SeoContentRoute({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const page = getSeoPage(slug);
  if (!page) notFound();

  const [brand, navigationItems] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getNavigationItems().catch(() => [])]);
  const schema = [
    organizationJsonLd(brand),
    localBusinessJsonLd(brand),
    websiteJsonLd(brand),
    webPageJsonLd({ title: page.title, description: page.description, path: `/${page.slug}` }),
    breadcrumbJsonLd([
      { name: "Home", path: "/" },
      { name: page.h1, path: `/${page.slug}` }
    ])
  ];

  return (
    <BrandTheme brand={brand}>
      <JsonLd data={schema} />
      <PublicHeader brand={brand} navigationItems={navigationItems} />
      <main className="bg-ivory text-espresso">
        <section className="bg-espresso px-5 py-20 text-ivory md:py-28 lg:px-8">
          <div className="mx-auto max-w-5xl">
            <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">{page.eyebrow}</p>
            <h1 className="mt-5 font-display text-5xl leading-tight md:text-7xl">{page.h1}</h1>
            <p className="mt-7 max-w-3xl text-lg leading-9 text-ivory/76">{page.intro}</p>
            <div className="mt-9 flex flex-wrap gap-4">
              <Link href="/glow-rituals" className="brand-button inline-flex items-center gap-3 bg-champagne px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-espresso transition hover:bg-ivory">
                Explore rituals
                <ArrowRight size={15} />
              </Link>
              <Link href="/campaigns/glow-consultation" className="brand-button border-b border-champagne pb-2 text-sm font-bold uppercase tracking-[0.16em] text-ivory transition hover:text-champagne">
                Book consultation
              </Link>
            </div>
          </div>
        </section>

        <section className="px-5 py-20 md:py-24 lg:px-8">
          <div className="mx-auto grid max-w-6xl gap-10 md:grid-cols-[1.35fr_0.65fr]">
            <div className="grid gap-8">
              {page.sections.map((section) => (
                <article key={section.title} className="border-b border-champagne/25 pb-8">
                  <h2 className="font-display text-3xl leading-tight md:text-4xl">{section.title}</h2>
                  <p className="mt-4 text-base leading-8 text-espresso/68">{section.body}</p>
                </article>
              ))}
            </div>
            <aside className="h-fit border border-champagne/25 bg-cream p-6">
              <h2 className="font-display text-2xl">Related searches answered</h2>
              <ul className="mt-5 grid gap-3 text-sm leading-6 text-espresso/70">
                {page.searchIntents.map((intent) => (
                  <li key={intent}>{intent}</li>
                ))}
              </ul>
              <div className="mt-8 border-t border-champagne/25 pt-6">
                <h2 className="font-display text-2xl">Continue exploring</h2>
                <div className="mt-5 grid gap-3">
                  {page.related.map((item) => (
                    <Link key={item} href={relatedHref(item)} className="inline-flex items-center justify-between gap-3 border-b border-champagne/25 py-2 text-sm font-semibold text-espresso transition hover:text-champagne">
                      {relatedLabel(item)}
                      <ArrowRight size={14} />
                    </Link>
                  ))}
                </div>
              </div>
            </aside>
          </div>
        </section>
      </main>
      <Footer brand={brand} navigationItems={navigationItems} />
    </BrandTheme>
  );
}

function relatedHref(slug: string) {
  if (slug === "contact") return "/contact";
  if (seoPageMap.has(slug)) return `/${slug}`;
  return `/glow-rituals/${slug}`;
}

function relatedLabel(slug: string) {
  const seoPage = seoPageMap.get(slug);
  if (seoPage) return seoPage.h1;
  if (slug === "contact") return "Contact The Glow Mission";
  return slug
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
