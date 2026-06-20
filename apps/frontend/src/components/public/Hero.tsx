"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import type { HeroSlide } from "@/types/cms";
import { ResponsiveImage } from "@/components/public/ResponsiveImage";

const autoplayMs = 7200;

export function Hero({ slides }: { slides: HeroSlide[] }) {
  const resolvedSlides = useMemo<HeroSlide[]>(() => slides, [slides]);
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);
  const reduceMotion = useReducedMotion();
  const active = resolvedSlides.length ? resolvedSlides[index % resolvedSlides.length] : null;
  const canNavigate = resolvedSlides.length > 1;

  useEffect(() => {
    if (resolvedSlides.length < 2 || paused || reduceMotion) return;
    const timer = window.setTimeout(() => setIndex((current) => (current + 1) % resolvedSlides.length), autoplayMs);
    return () => window.clearTimeout(timer);
  }, [index, paused, reduceMotion, resolvedSlides.length]);

  function showPrevious() {
    setIndex((current) => (current - 1 + resolvedSlides.length) % resolvedSlides.length);
  }

  function showNext() {
    setIndex((current) => (current + 1) % resolvedSlides.length);
  }

  if (!active) {
    return null;
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

      <div className="relative z-10 mx-auto flex min-h-[calc(100svh-76px)] max-w-7xl items-center px-5 py-14 md:py-20 lg:px-8">
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
              {canNavigate && (
                <div className="mt-7 flex items-center gap-3 md:hidden">
                  <HeroNavButton direction="previous" onClick={showPrevious} />
                  <HeroNavButton direction="next" onClick={showNext} />
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
      {canNavigate && (
        <div className="pointer-events-none absolute inset-x-8 top-1/2 z-20 hidden -translate-y-1/2 items-center justify-between md:flex lg:inset-x-10">
          <HeroNavButton direction="previous" onClick={showPrevious} desktop />
          <HeroNavButton direction="next" onClick={showNext} desktop />
        </div>
      )}
    </section>
  );
}

function HeroNavButton({
  direction,
  onClick,
  desktop = false
}: {
  direction: "previous" | "next";
  onClick: () => void;
  desktop?: boolean;
}) {
  const label = direction === "previous" ? "Previous hero slide" : "Next hero slide";
  const Icon = direction === "previous" ? ChevronLeft : ChevronRight;

  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      className={`pointer-events-auto inline-flex h-12 w-12 shrink-0 items-center justify-center border border-ivory/35 bg-espresso/45 text-ivory shadow-[0_18px_48px_rgba(0,0,0,0.24)] backdrop-blur transition hover:border-champagne hover:bg-champagne hover:text-espresso focus:outline-none focus:ring-4 focus:ring-champagne/25 ${
        desktop ? "h-14 w-14" : ""
      }`}
    >
      <Icon size={desktop ? 24 : 22} aria-hidden="true" />
    </button>
  );
}
