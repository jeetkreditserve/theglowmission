"use client";

/* eslint-disable @next/next/no-img-element */
import type { ImgHTMLAttributes } from "react";
import type { ImageVariantSet } from "@/types/cms";

type ResponsiveImageProps = Omit<ImgHTMLAttributes<HTMLImageElement>, "src" | "srcSet" | "sizes"> & {
  variants?: ImageVariantSet | null;
  src?: string | null;
  fallbackSrc: string;
  sizes: string;
};

export function ResponsiveImage({ variants, src, fallbackSrc, sizes, alt, ...props }: ResponsiveImageProps) {
  const webpSrcSet = buildSrcSet(variants?.webp);
  const jpegSrcSet = buildSrcSet(variants?.jpeg);
  const fallbackVariant = pickLargest(variants?.jpeg) || pickLargest(variants?.webp);
  const resolvedSrc = fallbackVariant || src || variants?.fallback_url || fallbackSrc;

  return (
    <picture>
      {webpSrcSet && <source type="image/webp" srcSet={webpSrcSet} sizes={sizes} />}
      {jpegSrcSet && <source type="image/jpeg" srcSet={jpegSrcSet} sizes={sizes} />}
      <img
        {...props}
        src={resolvedSrc}
        srcSet={jpegSrcSet || undefined}
        sizes={jpegSrcSet ? sizes : undefined}
        alt={alt}
        onError={(event) => {
          const image = event.currentTarget;
          if (!image.dataset.fallbackApplied) {
            image.dataset.fallbackApplied = "true";
            image.removeAttribute("srcset");
            image.src = fallbackSrc;
          }
          props.onError?.(event);
        }}
      />
    </picture>
  );
}

function buildSrcSet(variants?: ImageVariantSet["webp"] | null) {
  const entries = variants?.filter((variant) => variant.url).sort((a, b) => a.width - b.width) || [];
  if (!entries.length) return "";
  return entries.map((variant) => `${variant.url} ${variant.width}w`).join(", ");
}

function pickLargest(variants?: ImageVariantSet["webp"] | null) {
  const entries = variants?.filter((variant) => variant.url).sort((a, b) => b.width - a.width) || [];
  return entries[0]?.url || "";
}
