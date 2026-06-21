import type { BrandSettings, FAQ, Service } from "@/types/cms";
import { absoluteUrl, defaultLogoImage, defaultSeoDescription, defaultSocialImage, siteName, siteUrl, stableAssetUrl } from "@/lib/site";

type JsonLdNode = Record<string, unknown>;

function compact<T extends Record<string, unknown>>(value: T): T {
  return Object.fromEntries(
    Object.entries(value).filter(([, item]) => {
      if (item === null || item === undefined || item === "") return false;
      if (Array.isArray(item) && !item.length) return false;
      return true;
    })
  ) as T;
}

function sameAs(brand: BrandSettings) {
  const socialValues = Object.values(brand.social_links || {}).filter(Boolean);
  return Array.from(new Set([...(brand.same_as_links || []), ...socialValues]));
}

export function organizationJsonLd(brand: BrandSettings): JsonLdNode {
  return compact({
    "@type": "Organization",
    "@id": `${siteUrl()}#organization`,
    name: brand.site_title || siteName,
    url: siteUrl(),
    logo: stableAssetUrl(brand.logo_url, defaultLogoImage),
    description: brand.business_description || brand.mission_statement || defaultSeoDescription,
    sameAs: sameAs(brand)
  });
}

export function localBusinessJsonLd(brand: BrandSettings): JsonLdNode {
  const hasGeo = brand.latitude && brand.longitude;
  return compact({
    "@type": "HealthAndBeautyBusiness",
    "@id": `${siteUrl()}#local-business`,
    name: brand.site_title || siteName,
    url: siteUrl(),
    image: stableAssetUrl(brand.logo_url, defaultSocialImage),
    description: brand.business_description || defaultSeoDescription,
    email: brand.contact_email,
    telephone: brand.phone,
    priceRange: "INR 3599-8999",
    areaServed: [
      { "@type": "Place", name: "Chandivali" },
      { "@type": "Place", name: "Powai" },
      { "@type": "City", name: "Mumbai" }
    ],
    address: compact({
      "@type": "PostalAddress",
      streetAddress: brand.address,
      addressLocality: "Mumbai",
      addressRegion: "Maharashtra",
      addressCountry: "IN"
    }),
    geo: hasGeo
      ? {
          "@type": "GeoCoordinates",
          latitude: brand.latitude,
          longitude: brand.longitude
        }
      : undefined,
    openingHours: brand.opening_hours || [],
    sameAs: sameAs(brand)
  });
}

export function websiteJsonLd(brand: BrandSettings): JsonLdNode {
  return {
    "@type": "WebSite",
    "@id": `${siteUrl()}#website`,
    name: brand.site_title || siteName,
    url: siteUrl(),
    publisher: { "@id": `${siteUrl()}#organization` },
    inLanguage: "en-IN"
  };
}

export function webPageJsonLd({ title, description, path }: { title: string; description?: string; path: string }): JsonLdNode {
  const url = absoluteUrl(path);
  return {
    "@type": "WebPage",
    "@id": `${url}#webpage`,
    url,
    name: title,
    description: description || defaultSeoDescription,
    isPartOf: { "@id": `${siteUrl()}#website` },
    about: { "@id": `${siteUrl()}#local-business` },
    inLanguage: "en-IN"
  };
}

export function breadcrumbJsonLd(items: Array<{ name: string; path: string }>): JsonLdNode {
  return {
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: absoluteUrl(item.path)
    }))
  };
}

export function faqPageJsonLd(faqs: FAQ[]): JsonLdNode | null {
  const visible = faqs.filter((faq) => faq.question && faq.answer).slice(0, 10);
  if (!visible.length) return null;
  return {
    "@type": "FAQPage",
    mainEntity: visible.map((faq) => ({
      "@type": "Question",
      name: faq.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: faq.answer
      }
    }))
  };
}

export function serviceJsonLd(service: Service, brand: BrandSettings): JsonLdNode {
  const amount = service.sale_price_amount || service.price_amount || undefined;
  return compact({
    "@type": "Service",
    "@id": `${absoluteUrl(`/glow-rituals/${service.slug}`)}#service`,
    name: service.title,
    description: service.description || service.short_description,
    image: service.image_url ? stableAssetUrl(service.image_url, defaultSocialImage) : undefined,
    areaServed: brand.area_served || "Chandivali, Powai, Mumbai, India",
    provider: { "@id": `${siteUrl()}#local-business` },
    serviceType: "Natural facial ritual",
    offers: amount
      ? {
          "@type": "Offer",
          price: amount,
          priceCurrency: service.currency || "INR",
          url: absoluteUrl(`/glow-rituals/${service.slug}`),
          availability: "https://schema.org/InStock"
        }
      : undefined
  });
}
