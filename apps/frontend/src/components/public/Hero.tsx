"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import type { HeroSlide, Service } from "@/types/cms";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";

const autoplayMs = 7200;

export function Hero({ slides, services }: { slides: HeroSlide[]; services: Service[] }) {
  const resolvedSlides = useMemo<HeroSlide[]>(() => slides, [slides]);
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const [manualVersion, setManualVersion] = useState(0);
  const reduceMotion = useReducedMotion();
  const active = resolvedSlides.length ? resolvedSlides[index % resolvedSlides.length] : null;
  const featuredServices = services.slice(0, 3);

  useEffect(() => {
    if (resolvedSlides.length < 2 || paused || reduceMotion) return;
    const timer = window.setTimeout(() => setIndex((current) => (current + 1) % resolvedSlides.length), autoplayMs);
    return () => window.clearTimeout(timer);
  }, [index, manualVersion, paused, reduceMotion, resolvedSlides.length]);

  if (!active) {
    return null;
  }

  function go(direction: number) {
    setIndex((current) => (current + direction + resolvedSlides.length) % resolvedSlides.length);
    setManualVersion((current) => current + 1);
  }

  function selectSlide(slideIndex: number) {
    setIndex(slideIndex);
    setManualVersion((current) => current + 1);
  }

  return (
    <section
      className="relative overflow-hidden bg-espresso text-ivory"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocusCapture={() => setPaused(true)}
      onBlurCapture={() => setPaused(false)}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={active.id}
          initial={{ opacity: 0, scale: 1.04 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 1.02 }}
          transition={{ duration: 1.1, ease: "easeOut" }}
          className="absolute inset-0"
        >
          {(active.image_url || active.image_variants?.fallback_url) && (
            <ResponsiveImage
              src={active.image_url}
              variants={active.image_variants}
              alt={active.image_alt || active.title}
              sizes="100vw"
              loading={index === 0 ? "eager" : "lazy"}
              fetchPriority={index === 0 ? "high" : "auto"}
              decoding="async"
              className="h-full w-full object-cover"
            />
          )}
        </motion.div>
      </AnimatePresence>
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(37,29,24,0.86)_0%,rgba(37,29,24,0.68)_36%,rgba(37,29,24,0.24)_68%,rgba(37,29,24,0.06)_100%)]" />
      <div className="absolute inset-x-0 bottom-0 h-72 bg-gradient-to-t from-espresso via-espresso/72 to-transparent" />

      <div className="relative z-10 mx-auto grid min-h-[calc(100svh-76px)] max-w-7xl grid-rows-[1fr_auto] px-5 pb-6 pt-14 md:pt-20 lg:px-8">
        <div className="flex items-center py-10 md:py-14">
          <div className="max-w-3xl">
            {active.offer_label && <p className="mb-5 text-xs font-semibold uppercase tracking-[0.22em] text-champagne">{active.offer_label}</p>}
            <AnimatePresence mode="wait">
              <motion.div
                key={`copy-${active.id}`}
                initial={reduceMotion ? false : { opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                exit={reduceMotion ? undefined : { opacity: 0, y: -16 }}
                transition={{ duration: 0.65, ease: "easeOut" }}
              >
                <h1 className="font-display text-5xl leading-[1.02] text-ivory md:text-7xl lg:text-[6.2rem]">{active.title}</h1>
                <p className="mt-6 max-w-2xl text-base leading-8 text-ivory/82 md:text-xl">{active.subtitle}</p>
                {active.body && <p className="mt-3 max-w-xl text-sm leading-7 text-ivory/70 md:text-base">{active.body}</p>}
                <div className="mt-8 flex flex-wrap items-center gap-4">
                  {active.primary_cta_label && active.primary_cta_url && (
                    <Link href={active.primary_cta_url} className="brand-button group inline-flex items-center gap-3 bg-champagne px-7 py-4 text-sm font-bold text-espresso transition hover:bg-ivory">
                      {active.primary_cta_label}
                      <ArrowRight size={16} className="transition group-hover:translate-x-1" />
                    </Link>
                  )}
                  {active.secondary_cta_label && active.secondary_cta_url && (
                    <Link href={active.secondary_cta_url} className="brand-button border-b border-champagne/70 pb-2 text-sm font-bold text-ivory transition hover:text-champagne">
                      {active.secondary_cta_label}
                    </Link>
                  )}
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        <div className="border border-ivory/16 bg-espresso/62 p-3 shadow-[0_24px_80px_rgba(0,0,0,0.22)] backdrop-blur-xl">
          <div className="grid gap-4 lg:grid-cols-[auto_1fr] lg:items-stretch">
            <div className="flex items-center justify-between gap-3 lg:w-36 lg:flex-col lg:items-start lg:justify-center">
              <div className="flex items-center gap-2">
                <button aria-label="Previous slide" type="button" onClick={() => go(-1)} className="flex h-11 w-11 items-center justify-center border border-ivory/20 text-ivory transition hover:border-champagne hover:text-champagne">
                  <ChevronLeft size={18} />
                </button>
                <button aria-label="Next slide" type="button" onClick={() => go(1)} className="flex h-11 w-11 items-center justify-center border border-ivory/20 text-ivory transition hover:border-champagne hover:text-champagne">
                  <ChevronRight size={18} />
                </button>
              </div>
              <div className="flex items-center gap-2">
                {resolvedSlides.map((slide, slideIndex) => (
                  <button
                    key={slide.id}
                    type="button"
                    aria-label={`Show slide ${slideIndex + 1}`}
                    aria-current={slideIndex === index}
                    onClick={() => selectSlide(slideIndex)}
                    className={`h-1.5 w-7 transition ${slideIndex === index ? "bg-champagne" : "bg-ivory/28 hover:bg-ivory/55"}`}
                  />
                ))}
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {featuredServices.map((service) => (
                <Link key={service.id} href={service.cta_url || (service.booking_campaign_slug ? `/campaigns/${service.booking_campaign_slug}` : "/glow-rituals")} className="group border border-ivory/16 bg-ivory/[0.07] p-4 transition hover:border-champagne/70 hover:bg-ivory/[0.12]">
                  <p className="text-[0.68rem] font-bold uppercase tracking-[0.16em] text-champagne">{service.duration}</p>
                  <h2 className="mt-2 font-display text-xl text-ivory">{service.title}</h2>
                  <p className="mt-2 line-clamp-2 text-xs leading-5 text-ivory/64">{service.short_description}</p>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
