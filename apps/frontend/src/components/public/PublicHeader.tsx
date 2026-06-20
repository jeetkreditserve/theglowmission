"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import type { BrandSettings, SiteNavigationItem } from "@/types/cms";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";

export function PublicHeader({ brand, navigationItems }: { brand: BrandSettings; navigationItems: SiteNavigationItem[] }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const navItems = navigationItems.filter((item) => item.placement === "header");
  const cta = navigationItems.find((item) => item.placement === "header_cta");

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  return (
    <header className="sticky top-0 z-40 border-b border-champagne/25 bg-ivory/94 text-espresso backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-4 sm:gap-5 sm:px-5 lg:px-8">
        <Link href="/" className="flex min-w-0 flex-1 items-center gap-3 lg:flex-none">
          {brand.logo_url && (
            <ResponsiveImage
              src={brand.logo_url}
              variants={brand.logo_variants}
              alt={brand.site_title}
              sizes="44px"
              loading="eager"
              fetchPriority="high"
              className="h-11 w-11 rounded-full border border-champagne/35 object-cover"
            />
          )}
          <span className="display-title truncate text-sm leading-5 text-espresso md:text-base">{brand.site_title}</span>
        </Link>
        <nav className="hidden items-center gap-6 text-[12px] font-semibold uppercase tracking-[0.16em] text-espresso/64 lg:flex">
          {navItems.map((item) => (
            <Link key={item.id} href={item.url} target={item.open_in_new_tab ? "_blank" : undefined} className="transition hover:text-espresso">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          {cta && (
            <Link
              href={cta.url}
              target={cta.open_in_new_tab ? "_blank" : undefined}
              className="brand-button hidden border border-champagne bg-champagne px-5 py-3 text-xs font-bold text-espresso transition hover:bg-ivory sm:inline-flex"
            >
              {cta.label}
            </Link>
          )}
          <button
            type="button"
            aria-label={open ? "Close navigation" : "Open navigation"}
            aria-expanded={open}
            onClick={() => setOpen((current) => !current)}
            className="flex h-11 w-11 items-center justify-center border border-champagne/35 text-espresso transition hover:border-champagne hover:bg-cream lg:hidden"
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
      {open && (
        <nav className="border-t border-champagne/20 bg-ivory px-4 py-5 shadow-[0_24px_60px_rgba(37,29,24,0.12)] lg:hidden">
          <div className="mx-auto grid max-w-7xl gap-1 text-sm font-semibold uppercase tracking-[0.12em] text-espresso">
            {navItems.map((item) => (
              <Link key={item.id} href={item.url} target={item.open_in_new_tab ? "_blank" : undefined} className="border-b border-champagne/15 py-4">
                {item.label}
              </Link>
            ))}
            {cta && (
              <Link href={cta.url} target={cta.open_in_new_tab ? "_blank" : undefined} className="brand-button mt-4 inline-flex items-center justify-center bg-champagne px-5 py-4 text-xs font-bold text-espresso">
                {cta.label}
              </Link>
            )}
          </div>
        </nav>
      )}
    </header>
  );
}
