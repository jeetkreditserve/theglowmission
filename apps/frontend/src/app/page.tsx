import { Footer } from "@/components/public/Footer";
import { Hero } from "@/components/public/Hero";
import { BrandTheme } from "@/components/public/BrandTheme";
import { JsonLd } from "@/components/public/JsonLd";
import { PublicHeader } from "@/components/public/PublicHeader";
import { SectionRenderer } from "@/components/public/SectionRenderer";
import { fallbackBrand, getBrandSettings, getFAQs, getGallery, getHeroSlides, getNavigationItems, getPage, getServices, getTestimonials } from "@/lib/api";
import { cmsPageMetadata } from "@/lib/metadata";
import { faqPageJsonLd, localBusinessJsonLd, organizationJsonLd, webPageJsonLd, websiteJsonLd } from "@/lib/structured-data";

export const dynamic = "force-dynamic";

export function generateMetadata() {
  return cmsPageMetadata("home");
}

export default async function HomePage() {
  const [brand, navigationItems, page, services, gallery, slides, faqs, testimonials] = await Promise.all([
    getBrandSettings().catch(() => fallbackBrand()),
    getNavigationItems().catch(() => []),
    getPage("home").catch(() => null),
    getServices().catch(() => []),
    getGallery().catch(() => []),
    getHeroSlides().catch(() => []),
    getFAQs().catch(() => []),
    getTestimonials().catch(() => [])
  ]);

  return (
    <BrandTheme brand={brand}>
      <JsonLd
        data={[
          organizationJsonLd(brand),
          localBusinessJsonLd(brand),
          websiteJsonLd(brand),
          webPageJsonLd({
            title: page?.seo_title || "The Glow Mission",
            description: page?.seo_description || brand.seo_description,
            path: "/"
          }),
          ...(faqPageJsonLd(faqs) ? [faqPageJsonLd(faqs) as Record<string, unknown>] : [])
        ]}
      />
      <PublicHeader brand={brand} navigationItems={navigationItems} />
      <main>
        <Hero slides={slides} />
        <SectionRenderer sections={page?.sections || []} services={services} gallery={gallery} faqs={faqs} testimonials={testimonials} />
      </main>
      <Footer brand={brand} navigationItems={navigationItems} />
    </BrandTheme>
  );
}
