export const siteName = "The Glow Mission";

export const defaultSeoDescription =
  "The Glow Mission is a boutique facial wellness studio in Chandivali and Powai, Mumbai, offering natural facial rituals, facial massage, face yoga, gua sha, and glow treatments.";

export const defaultLogoImage = "/reference/glow-mission-logo-3d.png";
export const defaultSocialImage = "/reference/glow-mission-post-1.png";

export function siteUrl() {
  return (process.env.NEXT_PUBLIC_SITE_URL || "https://theglowmission.com").replace(/\/+$/, "");
}

export function absoluteUrl(path = "/") {
  if (/^https?:\/\//i.test(path)) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${siteUrl()}${normalized}`;
}

export function stableAssetUrl(path: string | null | undefined, fallback = defaultSocialImage) {
  const value = path || fallback;
  if (isPresignedUrl(value)) return absoluteUrl(fallback);
  return absoluteUrl(value);
}

export function canonicalPathForCmsSlug(slug: string) {
  return slug === "home" ? "/" : `/${slug}`;
}

function isPresignedUrl(value: string) {
  return /[?&]X-Amz-/i.test(value) || /[?&]Expires=/i.test(value) || /[?&]Signature=/i.test(value);
}
