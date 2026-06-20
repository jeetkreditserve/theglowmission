import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, getBrandSettings, getGallery } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function GalleryPage() {
  const [brand, gallery] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getGallery().catch(() => [])]);
  const images = gallery.length
    ? gallery
    : [
        {
          id: 1,
          title: "The Glow Mission",
          alt_text: "The Glow Mission natural skincare composition",
          image_url: "/reference/glow-mission-post-1.png",
          caption: "Skin that glows. Confidence that shows.",
          active: true,
          ordering: 0
        }
      ];

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="bg-ivory">
        <section className="mx-auto max-w-7xl px-5 py-20 lg:px-8">
          <p className="display-title text-sm text-champagne">Gallery</p>
          <h1 className="mt-5 font-display text-5xl leading-tight text-espresso md:text-7xl">Warm natural textures.</h1>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {images.map((image) => (
              <figure key={image.id} className="border border-champagne/25 bg-cream p-3">
                <img src={image.image_url || "/reference/glow-mission-post-1.png"} alt={image.alt_text || image.title} className="aspect-square w-full object-cover" />
                <figcaption className="px-2 py-4 text-sm text-espresso/64">{image.caption}</figcaption>
              </figure>
            ))}
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
