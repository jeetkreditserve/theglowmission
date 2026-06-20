import { Footer } from "@/components/public/Footer";
import { Hero } from "@/components/public/Hero";
import { PublicHeader } from "@/components/public/PublicHeader";
import { SectionRenderer } from "@/components/public/SectionRenderer";
import { fallbackBrand, fallbackServices, getBrandSettings, getGallery, getPage, getServices } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [brand, page, services, gallery] = await Promise.all([
    getBrandSettings().catch(() => fallbackBrand()),
    getPage("home").catch(() => null),
    getServices().catch(() => fallbackServices),
    getGallery().catch(() => [])
  ]);
  const hero = page?.sections.find((section) => section.section_type === "hero");

  return (
    <>
      <PublicHeader brand={brand} />
      <main>
        <Hero brand={brand} section={hero} services={services} />
        <SectionRenderer sections={page?.sections || []} services={services} gallery={gallery} />
      </main>
      <Footer brand={brand} />
    </>
  );
}
