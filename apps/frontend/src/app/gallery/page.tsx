import { Footer } from "@/components/public/Footer";
import { PublicHeader } from "@/components/public/PublicHeader";
import { fallbackBrand, getBrandSettings, getGallery } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function GalleryPage() {
  const [brand, gallery] = await Promise.all([getBrandSettings().catch(() => fallbackBrand()), getGallery().catch(() => [])]);
  const images = gallery.length
    ? gallery
    : [
        { id: 1, title: "Signature ritual", alt_text: "Luxury facial massage", image_url: "/generated/glow-service-signature.png", caption: "A quiet hour of massage, touch, and rest.", active: true, ordering: 0 },
        { id: 2, title: "Botanical textures", alt_text: "Natural facial ingredients", image_url: "/generated/glow-service-natural-facial.png", caption: "Honey, cucumber, citrus, herbs, and warm towels.", active: true, ordering: 1 },
        { id: 3, title: "Face yoga", alt_text: "Guided face yoga", image_url: "/generated/glow-service-face-yoga.png", caption: "Gentle movement and lifting-focused care.", active: true, ordering: 2 }
      ];

  return (
    <>
      <PublicHeader brand={brand} />
      <main className="bg-cream">
        <section className="mx-auto max-w-7xl px-5 py-24 lg:px-8">
          <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">Gallery</p>
          <h1 className="mt-5 max-w-4xl font-display text-5xl leading-tight text-espresso md:text-7xl">The visual language of a slower glow ritual.</h1>
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {images.map((image, index) => (
              <figure key={image.id} className={index % 3 === 1 ? "lg:mt-12" : index % 3 === 2 ? "lg:mt-24" : ""}>
                <img src={image.image_url || "/generated/glow-service-signature.png"} alt={image.alt_text || image.title} className="aspect-[4/5] w-full object-cover shadow-[0_24px_70px_rgba(37,29,24,0.12)]" />
                <figcaption className="px-1 py-4 text-sm leading-6 text-espresso/64">{image.caption}</figcaption>
              </figure>
            ))}
          </div>
        </section>
      </main>
      <Footer brand={brand} />
    </>
  );
}
