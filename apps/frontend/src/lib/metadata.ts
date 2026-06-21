import type { Metadata } from "next";
import { getPage } from "@/lib/api";
import { absoluteUrl, canonicalPathForCmsSlug, defaultSeoDescription, defaultSocialImage, siteName, stableAssetUrl } from "@/lib/site";

export function pageMetadata({
  title,
  description,
  path,
  image = defaultSocialImage,
  type = "website"
}: {
  title: string;
  description?: string;
  path: string;
  image?: string | null;
  type?: "website" | "article";
}): Metadata {
  const resolvedDescription = description || defaultSeoDescription;
  const url = absoluteUrl(path);
  const imageUrl = stableAssetUrl(image, defaultSocialImage);
  return {
    title: { absolute: title },
    description: resolvedDescription,
    alternates: {
      canonical: url
    },
    robots: {
      index: true,
      follow: true
    },
    openGraph: {
      title,
      description: resolvedDescription,
      url,
      siteName,
      type,
      images: [
        {
          url: imageUrl,
          width: 1254,
          height: 1254,
          alt: `${siteName} natural facial ritual`
        }
      ],
      locale: "en_IN"
    },
    twitter: {
      card: "summary_large_image",
      title,
      description: resolvedDescription,
      images: [imageUrl]
    }
  };
}

export async function cmsPageMetadata(slug: string): Promise<Metadata> {
  const page = await getPage(slug).catch(() => null);
  if (!page) {
    return pageMetadata({
      title: siteName,
      description: defaultSeoDescription,
      path: canonicalPathForCmsSlug(slug)
    });
  }
  return pageMetadata({
    title: page.seo_title || `${page.title} | ${siteName}`,
    description: page.seo_description || undefined,
    path: canonicalPathForCmsSlug(slug)
  });
}
