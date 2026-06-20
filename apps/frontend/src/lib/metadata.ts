import type { Metadata } from "next";
import { getPage } from "@/lib/api";

export async function cmsPageMetadata(slug: string): Promise<Metadata> {
  const page = await getPage(slug).catch(() => null);
  if (!page) return {};
  return {
    title: page.seo_title || page.title,
    description: page.seo_description || undefined
  };
}
