import { getSeoIndex } from "@/lib/api";
import { seoPages } from "@/lib/seo-content";
import { absoluteUrl } from "@/lib/site";

export const dynamic = "force-dynamic";

type SitemapItem = {
  path: string;
  updated_at?: string;
  priority?: number;
};

export async function GET() {
  const cmsItems = await getSeoIndex().catch(() => [] as SitemapItem[]);
  const seoItems: SitemapItem[] = seoPages.map((page) => ({
    path: `/${page.slug}`,
    priority: page.slug === "what-is-the-glow-mission" ? 0.9 : 0.7
  }));

  const items = dedupeByPath([...cmsItems, ...seoItems]);
  const updated = new Date().toISOString();
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${items
    .map((item) => urlEntry(item, updated))
    .join("\n")}\n</urlset>\n`;

  return new Response(body, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=300, s-maxage=3600, stale-while-revalidate=86400"
    }
  });
}

function dedupeByPath(items: SitemapItem[]) {
  const seen = new Map<string, SitemapItem>();
  items.forEach((item) => {
    if (!item.path) return;
    seen.set(item.path, { ...seen.get(item.path), ...item });
  });
  return Array.from(seen.values()).sort((a, b) => a.path.localeCompare(b.path));
}

function urlEntry(item: SitemapItem, fallbackDate: string) {
  const lastmod = item.updated_at || fallbackDate;
  const priority = typeof item.priority === "number" ? item.priority.toFixed(2) : "0.60";
  return `  <url>\n    <loc>${escapeXml(absoluteUrl(item.path))}</loc>\n    <lastmod>${escapeXml(lastmod)}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>${priority}</priority>\n  </url>`;
}

function escapeXml(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
