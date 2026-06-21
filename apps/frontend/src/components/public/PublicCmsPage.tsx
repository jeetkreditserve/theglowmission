import { notFound } from "next/navigation";
import { BrandTheme } from "@/components/public/BrandTheme";
import { Footer } from "@/components/public/Footer";
import { JsonLd } from "@/components/public/JsonLd";
import { PublicHeader } from "@/components/public/PublicHeader";
import { SectionRenderer } from "@/components/public/SectionRenderer";
import { fallbackBrand, getBrandSettings, getFAQs, getGallery, getNavigationItems, getPage, getServices, getTestimonials } from "@/lib/api";
import { canonicalPathForCmsSlug } from "@/lib/site";
import { breadcrumbJsonLd, faqPageJsonLd, localBusinessJsonLd, organizationJsonLd, webPageJsonLd, websiteJsonLd } from "@/lib/structured-data";

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

  const faqSchema = slug === "contact" || slug === "glow-rituals" ? faqPageJsonLd(faqs) : null;

  return (
    <BrandTheme brand={brand}>
      <JsonLd
        data={[
          organizationJsonLd(brand),
          localBusinessJsonLd(brand),
          websiteJsonLd(brand),
          webPageJsonLd({
            title: page.seo_title || page.title,
            description: page.seo_description || brand.seo_description,
            path: canonicalPathForCmsSlug(slug)
          }),
          breadcrumbJsonLd([
            { name: "Home", path: "/" },
            { name: page.title, path: canonicalPathForCmsSlug(slug) }
          ]),
          ...(faqSchema ? [faqSchema] : [])
        ]}
      />
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
