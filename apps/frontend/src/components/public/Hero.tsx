"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import type { BrandSettings, HeroSlide, Service } from "@/types/cms";

const fallbackImages = ["/generated/glow-hero-facial-massage.png", "/generated/glow-hero-offer.png"];

export function Hero({ brand, slides, services }: { brand: BrandSettings; slides: HeroSlide[]; services: Service[] }) {
  const resolvedSlides = useMemo<HeroSlide[]>(
    () =>
      slides.length
        ? slides
        : [
            {
              id: 1,
              title: brand.tagline,
              subtitle: brand.essence,
              body: "Come in for one peaceful hour. Leave feeling rested, lifted, and beautifully looked after.",
              image_url: fallbackImages[0],
              image_alt: "Luxury facial massage ritual",
              offer_label: "Signature consultation",
              primary_cta_label: "Book a consultation",
              primary_cta_url: "/campaigns/glow-consultation",
              secondary_cta_label: "Explore rituals",
              secondary_cta_url: "/services",
              linked_campaign: null,
              campaign_slug: "",
              campaign_title: "",
              starts_at: null,
              ends_at: null,
              active: true,
              is_active_now: true,
              ordering: 0,
              config: {}
            }
          ],
    [brand, slides]
  );
  const [index, setIndex] = useState(0);
  const active = resolvedSlides[index % resolvedSlides.length];
  const featuredServices = services.slice(0, 3);

  useEffect(() => {
    if (resolvedSlides.length < 2) return;
    const timer = window.setInterval(() => setIndex((current) => (current + 1) % resolvedSlides.length), 6800);
    return () => window.clearInterval(timer);
  }, [resolvedSlides.length]);

  function go(direction: number) {
    setIndex((current) => (current + direction + resolvedSlides.length) % resolvedSlides.length);
  }

  return (
    <section className="relative min-h-[calc(100vh-0px)] overflow-hidden bg-espresso text-ivory">
      <AnimatePresence mode="wait">
        <motion.img
          key={active.id}
          src={active.image_url || fallbackImages[index % fallbackImages.length]}
          alt={active.image_alt || active.title}
          initial={{ opacity: 0, scale: 1.04 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 1.02 }}
          transition={{ duration: 1.1, ease: "easeOut" }}
          className="absolute inset-0 h-full w-full object-cover"
        />
      </AnimatePresence>
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(37,29,24,0.88)_0%,rgba(37,29,24,0.62)_38%,rgba(37,29,24,0.18)_70%,rgba(37,29,24,0.28)_100%)]" />
      <div className="absolute inset-x-0 bottom-0 h-52 bg-gradient-to-t from-espresso via-espresso/70 to-transparent" />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col justify-center px-5 pb-40 pt-32 lg:px-8">
        <div className="max-w-3xl">
          {active.offer_label && <p className="mb-6 text-xs font-semibold uppercase tracking-[0.28em] text-champagne">{active.offer_label}</p>}
          <AnimatePresence mode="wait">
            <motion.div
              key={`copy-${active.id}`}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.65, ease: "easeOut" }}
            >
              <h1 className="font-display text-5xl leading-[0.98] text-ivory md:text-7xl lg:text-[6.8rem]">{active.title}</h1>
              <p className="mt-7 max-w-2xl text-lg leading-8 text-ivory/80 md:text-xl">{active.subtitle}</p>
              {active.body && <p className="mt-4 max-w-xl text-base leading-7 text-ivory/68">{active.body}</p>}
              <div className="mt-9 flex flex-wrap items-center gap-4">
                <Link href={active.primary_cta_url || "/campaigns/glow-consultation"} className="group inline-flex items-center gap-3 bg-champagne px-7 py-4 text-sm font-bold uppercase tracking-[0.16em] text-espresso transition hover:bg-ivory">
                  {active.primary_cta_label || "Book a consultation"}
                  <ArrowRight size={16} className="transition group-hover:translate-x-1" />
                </Link>
                {active.secondary_cta_label && (
                  <Link href={active.secondary_cta_url || "/services"} className="border-b border-champagne/70 pb-2 text-sm font-bold uppercase tracking-[0.16em] text-ivory transition hover:text-champagne">
                    {active.secondary_cta_label}
                  </Link>
                )}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      <div className="absolute bottom-8 left-1/2 z-20 w-[min(92vw,80rem)] -translate-x-1/2">
        <div className="grid gap-4 border border-ivory/15 bg-espresso/60 p-3 backdrop-blur-xl md:grid-cols-[auto_1fr] md:items-stretch">
          <div className="flex items-center gap-2 px-1">
            <button aria-label="Previous slide" type="button" onClick={() => go(-1)} className="flex h-11 w-11 items-center justify-center border border-ivory/20 text-ivory transition hover:border-champagne hover:text-champagne">
              <ChevronLeft size={18} />
            </button>
            <button aria-label="Next slide" type="button" onClick={() => go(1)} className="flex h-11 w-11 items-center justify-center border border-ivory/20 text-ivory transition hover:border-champagne hover:text-champagne">
              <ChevronRight size={18} />
            </button>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            {featuredServices.map((service) => (
              <Link key={service.id} href={service.cta_url || "/services"} className="group border border-ivory/12 bg-ivory/[0.06] p-4 transition hover:border-champagne/70 hover:bg-ivory/[0.11]">
                <p className="text-[0.68rem] font-bold uppercase tracking-[0.18em] text-champagne">{service.duration}</p>
                <h2 className="mt-2 font-display text-xl text-ivory">{service.title}</h2>
                <p className="mt-2 line-clamp-2 text-xs leading-5 text-ivory/62">{service.short_description}</p>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
