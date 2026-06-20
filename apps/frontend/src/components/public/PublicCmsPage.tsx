import { notFound } from "next/navigation";
import { BrandTheme } from "@/components/public/BrandTheme";
import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { SectionRenderer } from "@/components/public/SectionRenderer";
import { fallbackBrand, getBrandSettings, getFAQs, getGallery, getNavigationItems, getPage, getServices, getTestimonials } from "@/lib/api";

export async function PublicCmsPage({ slug }: { slug: string }) {
  const [brand, navigationItems, page, services, gallery, faqs, testimonials] = await Promise.all([
    getBrandSettings().catch(() => fallbackBrand()),
    getNavigationItems().catch(() => []),
    getPage(slug).catch(() => null),
    getServices().catch(() => []),
    getGallery().catch(() => []),
    getFAQs().catch(() => []),
    getTestimonials().catch(() => [])
  ]);

  if (!page) {
    notFound();
  }

  return (
    <BrandTheme brand={brand}>
      <PublicHeader brand={brand} navigationItems={navigationItems} />
      <main>
        <SectionRenderer
          sections={page.sections || []}
          services={services}
          gallery={gallery}
          faqs={faqs}
          testimonials={testimonials}
          brand={brand}
          includeHeroSections
        />
      </main>
      <Footer brand={brand} navigationItems={navigationItems} />
    </BrandTheme>
  );
}
