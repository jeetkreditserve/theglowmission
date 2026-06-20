import { Footer } from "@/components/public/Footer";
import { BrandTheme } from "@/components/public/BrandTheme";
import { PublicHeader } from "@/components/public/PublicHeader";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";
import { fallbackBrand, getBrandSettings, getGallery } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function GalleryPage() {
  const [brand, gallery] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getGallery().catch(() => [])]);
  const images = gallery.length
    ? gallery
    : [
        { id: 1, title: "Signature ritual", alt_text: "Luxury facial massage", image_url: "/generated/glow-gallery-massage-detail.webp", caption: "A quiet hour of massage, touch, and rest.", active: true, ordering: 0 },
        { id: 2, title: "Botanical textures", alt_text: "Natural facial ingredients", image_url: "/generated/glow-gallery-botanicals.webp", caption: "Honey, cucumber, citrus, herbs, and warm towels.", active: true, ordering: 1 },
        { id: 3, title: "Treatment room calm", alt_text: "Prepared boutique spa treatment bed", image_url: "/generated/glow-gallery-treatment-room.webp", caption: "A quiet room prepared for slow facial care.", active: true, ordering: 2 }
      ];

  return (
    <BrandTheme brand={brand}>
      <PublicHeader brand={brand} />
      <main className="bg-cream">
        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">Gallery</p>
          <h1 className="mt-5 max-w-4xl font-display text-5xl leading-tight text-espresso md:text-7xl">The visual language of a slower glow ritual.</h1>
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {images.map((image, index) => (
              <figure key={image.id} className={index % 3 === 1 ? "lg:mt-12" : index % 3 === 2 ? "lg:mt-24" : ""}>
                <ResponsiveImage
                  src={image.image_url || "/generated/glow-gallery-massage-detail.webp"}
                  variants={image.image_variants}
                  fallbackSrc="/generated/glow-gallery-massage-detail.webp"
                  alt={image.alt_text || image.title}
                  sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                  loading={index === 0 ? "eager" : "lazy"}
                  fetchPriority={index === 0 ? "high" : "auto"}
                  decoding="async"
                  className="aspect-[4/5] w-full object-cover shadow-[0_24px_70px_rgba(37,29,24,0.12)]"
                />
                <figcaption className="px-1 py-4 text-sm leading-6 text-espresso/64">{image.caption}</figcaption>
              </figure>
            ))}
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </BrandTheme>
  );
}
