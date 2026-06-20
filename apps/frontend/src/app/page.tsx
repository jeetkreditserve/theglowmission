import { Footer } from "@/components/public/Footer";
import { Hero } from "@/components/public/Hero";
import { PublicHeader } from "@/components/public/PublicHeader";
import { SectionRenderer } from "@/components/public/SectionRenderer";
import { fallbackBrand, fallbackServices, getBrandSettings, getFAQs, getGallery, getHeroSlides, getPage, getServices, getTestimonials } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [brand, page, services, gallery, slides, faqs, testimonials] = await Promise.all([
    getBrandSettings().catch(() => fallbackBrand()),
    getPage("home").catch(() => null),
    getServices().catch(() => fallbackServices),
    getGallery().catch(() => []),
    getHeroSlides().catch(() => []),
    getFAQs().catch(() => []),
    getTestimonials().catch(() => [])
  ]);

  return (
    <>
      <PublicHeader brand={brand} />
      <main>
        <Hero brand={brand} slides={slides} services={services} />
        <SectionRenderer sections={page?.sections || []} services={services} gallery={gallery} faqs={faqs} testimonials={testimonials} />
      </main>
      <Footer brand={brand} />
    </>
  );
}
