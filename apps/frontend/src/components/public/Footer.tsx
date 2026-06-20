import Link from "next/link";
import type { BrandSettings } from "@/types/cms";

export function Footer({ brand }: { brand: BrandSettings }) {
  return (
    <footer className="border-t border-champagne/25 bg-espresso text-ivory">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-12 md:grid-cols-[1.4fr_1fr_1fr] lg:px-8">
        <div>
          <p className="display-title text-xl">{brand.site_title}</p>
          <p className="mt-4 max-w-xl text-sm leading-7 text-ivory/72">{brand.essence}</p>
        </div>
        <div className="text-sm leading-8 text-ivory/75">
          <Link href="/about" className="block hover:text-white">
            About
          </Link>
          <Link href="/services" className="block hover:text-white">
            Services
          </Link>
          <Link href="/gallery" className="block hover:text-white">
            Gallery
          </Link>
          <Link href="/contact" className="block hover:text-white">
            Contact
          </Link>
        </div>
        <div className="text-sm leading-8 text-ivory/75">
          <p>{brand.contact_email}</p>
          <p>{brand.instagram_handle}</p>
          <p className="pt-3 text-xs uppercase tracking-[0.18em] text-champagne">{brand.tagline}</p>
        </div>
      </div>
    </footer>
  );
}

