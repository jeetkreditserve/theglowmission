import Link from "next/link";
import type { BrandSettings, SiteNavigationItem } from "@/types/cms";

export function Footer({ brand, navigationItems }: { brand: BrandSettings; navigationItems: SiteNavigationItem[] }) {
  const footerLinks = navigationItems.filter((item) => item.placement === "footer");
  const footerCta = navigationItems.find((item) => item.placement === "footer_cta");
  const socialLinks = navigationItems.filter((item) => item.placement === "social");
  const contactRows = [brand.contact_email, brand.phone, brand.address].filter(Boolean);

  return (
    <footer className="border-t border-champagne/20 bg-[#1d1512] text-ivory">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-16 md:grid-cols-[1.4fr_1fr_1fr] lg:px-8">
        <div>
          <p className="display-title text-2xl">{brand.site_title}</p>
          <p className="mt-5 max-w-xl text-sm leading-7 text-ivory/68">{brand.essence}</p>
          {footerCta && (
            <Link href={footerCta.url} target={footerCta.open_in_new_tab ? "_blank" : undefined} className="mt-7 inline-block border-b border-champagne pb-2 text-xs font-bold uppercase tracking-[0.18em] text-champagne">
              {footerCta.label}
            </Link>
          )}
        </div>
        <div className="text-sm leading-8 text-ivory/70">
          {footerLinks.map((item) => (
            <Link key={item.id} href={item.url} target={item.open_in_new_tab ? "_blank" : undefined} className="block hover:text-white">
              {item.label}
            </Link>
          ))}
        </div>
        <div className="text-sm leading-8 text-ivory/70">
          {contactRows.map((row) => (
            <p key={row}>{row}</p>
          ))}
          {socialLinks.map((item) => (
            <Link key={item.id} href={item.url} target={item.open_in_new_tab ? "_blank" : undefined} className="block hover:text-white">
              {item.label}
            </Link>
          ))}
          <p className="pt-3 text-xs uppercase tracking-[0.18em] text-champagne">{brand.tagline}</p>
        </div>
      </div>
    </footer>
  );
}
