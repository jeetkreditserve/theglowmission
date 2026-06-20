import { Footer } from "@/components/public/Footer";
import { Hero } from "@/components/public/Hero";
import { BrandTheme } from "@/components/public/BrandTheme";
import { PublicHeader } from "@/components/public/PublicHeader";
import { SectionRenderer } from "@/components/public/SectionRenderer";
import { fallbackBrand, getBrandSettings, getFAQs, getGallery, getHeroSlides, getNavigationItems, getPage, getServices, getTestimonials } from "@/lib/api";
import { cmsPageMetadata } from "@/lib/metadata";

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
      <PublicHeader brand={brand} navigationItems={navigationItems} />
      <main>
        <Hero slides={slides} />
        <SectionRenderer sections={page?.sections || []} services={services} gallery={gallery} faqs={faqs} testimonials={testimonials} />
      </main>
      <Footer brand={brand} navigationItems={navigationItems} />
    </BrandTheme>
  );
}
