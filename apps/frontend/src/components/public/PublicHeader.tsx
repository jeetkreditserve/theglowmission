import Link from "next/link";
import type { BrandSettings } from "@/types/cms";
import { SafeImage } from "@/components/public/SafeImage";

const navItems = [
  ["Home", "/"],
  ["About", "/about"],
  ["Services", "/services"],
  ["Glow Rituals", "/glow-rituals"],
  ["Gallery", "/gallery"],
  ["Contact", "/contact"]
];

export function PublicHeader({ brand }: { brand: BrandSettings }) {
  return (
    <header className="sticky top-0 z-40 border-b border-champagne/20 bg-espresso/92 text-ivory backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-4 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <SafeImage
            src={brand.logo_url || "/reference/glow-mission-logo-3d.png"}
            fallbackSrc="/reference/glow-mission-logo-3d.png"
            alt={brand.site_title}
            className="h-11 w-11 rounded-full border border-champagne/30 object-cover"
          />
          <span className="display-title text-sm leading-5 text-ivory md:text-base">{brand.site_title}</span>
        </Link>
        <nav className="hidden items-center gap-6 text-[12px] font-semibold uppercase tracking-[0.16em] text-ivory/70 lg:flex">
          {navItems.map(([label, href]) => (
            <Link key={href} href={href} className="transition hover:text-champagne">
              {label}
            </Link>
          ))}
        </nav>
        <Link
          href="/campaigns/glow-consultation"
          className="border border-champagne bg-champagne px-5 py-3 text-xs font-bold uppercase tracking-[0.18em] text-espresso transition hover:bg-ivory"
        >
          Book
        </Link>
      </div>
    </header>
  );
}
