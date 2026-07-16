import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, Check } from "lucide-react";
import { BrandTheme } from "@/components/public/BrandTheme";
import { Footer } from "@/components/public/Footer";
import { JsonLd } from "@/components/public/JsonLd";
import { PublicHeader } from "@/components/public/PublicHeader";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";
import { RitualBookingButton } from "@/components/public/RitualBookingButton";
import { fallbackBrand, getBrandSettings, getNavigationItems, getService } from "@/lib/api";
import { pageMetadata } from "@/lib/metadata";
import { breadcrumbJsonLd, localBusinessJsonLd, organizationJsonLd, serviceJsonLd, webPageJsonLd, websiteJsonLd } from "@/lib/structured-data";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const service = await getService(slug).catch(() => null);
  if (!service) return {};
  return pageMetadata({
    title: `${service.title} | Natural Facial Ritual in Mumbai`,
    description: service.description || service.short_description,
    path: `/glow-rituals/${service.slug}`,
    image: service.image_url
  });
}

export default async function ServiceDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [brand, navigationItems, service] = await Promise.all([
    getBrandSettings().catch(() => fallbackBrand()),
    getNavigationItems().catch(() => []),
    getService(slug).catch(() => null)
  ]);
  if (!service) notFound();

  const schema = [
    organizationJsonLd(brand),
    localBusinessJsonLd(brand),
    websiteJsonLd(brand),
    serviceJsonLd(service, brand),
    webPageJsonLd({
      title: `${service.title} | The Glow Mission`,
      description: service.description || service.short_description,
      path: `/glow-rituals/${service.slug}`
    }),
    breadcrumbJsonLd([
      { name: "Home", path: "/" },
      { name: "Glow Rituals", path: "/glow-rituals" },
      { name: service.title, path: `/glow-rituals/${service.slug}` }
    ])
  ];

  return (
    <BrandTheme brand={brand}>
      <JsonLd data={schema} />
      <PublicHeader brand={brand} navigationItems={navigationItems} />
      <main className="bg-ivory text-espresso">
        <section className="bg-espresso px-5 py-20 text-ivory md:py-28 lg:px-8">
          <div className="mx-auto grid max-w-7xl gap-12 md:grid-cols-[0.9fr_1.1fr] md:items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.26em] text-champagne">Glow ritual</p>
              <h1 className="mt-5 font-display text-5xl leading-tight md:text-7xl">{service.title}</h1>
              <p className="mt-6 max-w-2xl text-lg leading-9 text-ivory/76">{service.description || service.short_description}</p>
              <div className="mt-8 flex flex-wrap items-center gap-4">
                <RitualBookingButton service={service} className="brand-button inline-flex items-center gap-3 bg-champagne px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-espresso transition hover:bg-ivory">
                  Book this ritual
                  <ArrowRight size={15} />
                </RitualBookingButton>
                <Link href="/glow-rituals" className="brand-button border-b border-champagne pb-2 text-sm font-bold uppercase tracking-[0.16em] text-ivory transition hover:text-champagne">
                  View all rituals
                </Link>
              </div>
            </div>
            {service.image_url && (
              <ResponsiveImage
                src={service.image_url}
                variants={service.image_variants}
                alt={service.image_alt || service.title}
                sizes="(min-width: 768px) 45vw, 100vw"
                loading="eager"
                fetchPriority="high"
                decoding="async"
                className="aspect-[4/5] w-full object-cover shadow-[0_34px_90px_rgba(0,0,0,0.22)]"
              />
            )}
          </div>
        </section>

        <section className="px-5 py-20 md:py-24 lg:px-8">
          <div className="mx-auto grid max-w-7xl gap-10 md:grid-cols-[0.75fr_1.25fr]">
            <aside className="h-fit border border-champagne/25 bg-cream p-6">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-champagne">{service.duration}</p>
              {formatPrice(service.currency, service.sale_price_amount || service.price_amount) && (
                <p className="mt-4 font-display text-5xl">{formatPrice(service.currency, service.sale_price_amount || service.price_amount)}</p>
              )}
              {service.price_note && <p className="mt-4 text-sm leading-7 text-espresso/66">{service.price_note}</p>}
              <p className="mt-7 text-sm leading-7 text-espresso/64">
                Every Glow Mission facial can be thoughtfully adapted to your skin needs. Share allergies, sensitivities, and comfort preferences before the session.
              </p>
            </aside>
            <div>
              <h2 className="font-display text-4xl leading-tight md:text-5xl">Ritual flow</h2>
              {!!service.inclusions?.length && (
                <ul className="mt-8 grid gap-4 md:grid-cols-2">
                  {service.inclusions.map((item) => (
                    <li key={item} className="flex items-start gap-3 border border-champagne/20 bg-white/55 p-4 text-sm leading-7 text-espresso/72">
                      <Check size={17} className="mt-1 shrink-0 text-sage" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              )}
              <div className="mt-12 border-t border-champagne/25 pt-8">
                <h2 className="font-display text-3xl">Who this ritual is for</h2>
                <p className="mt-4 max-w-3xl text-base leading-8 text-espresso/68">
                  This ritual is for clients around Chandivali, Powai, and Mumbai who want natural facial care, facial massage, visible glow, and a calmer beauty experience. It is a wellness and beauty ritual, not a medical dermatology procedure.
                </p>
                <div className="mt-7 flex flex-wrap gap-4">
                  <Link href="/facial-massage-mumbai" className="border-b border-champagne pb-2 text-sm font-bold uppercase tracking-[0.16em] text-espresso transition hover:text-champagne">
                    Facial massage
                  </Link>
                  <Link href="/natural-facial-mumbai" className="border-b border-champagne pb-2 text-sm font-bold uppercase tracking-[0.16em] text-espresso transition hover:text-champagne">
                    Natural facial care
                  </Link>
                  <Link href="/facial-in-powai" className="border-b border-champagne pb-2 text-sm font-bold uppercase tracking-[0.16em] text-espresso transition hover:text-champagne">
                    Powai facials
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer brand={brand} navigationItems={navigationItems} />
    </BrandTheme>
  );
}

function formatPrice(currency: string, value: string | null) {
  if (!value) return "";
  const amount = Number(value);
  if (!Number.isFinite(amount)) return value;
  if (currency === "INR") return `INR ${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  return `${currency} ${amount.toLocaleString()}`;
}
