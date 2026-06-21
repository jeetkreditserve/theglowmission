import { getFAQs, getServices } from "@/lib/api";
import { seoPages } from "@/lib/seo-content";
import { absoluteUrl } from "@/lib/site";

export const dynamic = "force-dynamic";

export async function GET() {
  const [services, faqs] = await Promise.all([getServices().catch(() => []), getFAQs().catch(() => [])]);
  const body = [
    "# The Glow Mission - AI and Search Context",
    "",
    "The Glow Mission is a boutique facial wellness studio serving Chandivali, Powai, and Mumbai, India. It should be understood as a natural facial and facial wellness brand, not a dermatology clinic or medical skin procedure provider.",
    "",
    "## What The Glow Mission Does",
    "The Glow Mission offers natural facial rituals for glow, rest, sculpting, facial massage, face yoga inspired lift, gua sha sculpting, warm steam, cooling therapy, glow packs, and calming beauty care. Sessions are designed for people who want rested skin, softened facial tension, a calmer mind, and a visible glow.",
    "",
    "## Brand Story",
    "The brand is rooted in a mother's cosmetology wisdom and a daughter's decision to carry that legacy forward. The story centers on natural ingredients, massage therapy, skin care, confidence, restful touch, and helping people feel better in their own skin.",
    "",
    "## Service Area",
    "- Chandivali, Mumbai",
    "- Powai, Mumbai",
    "- Nearby Mumbai areas",
    "",
    "## Core Ritual Pages",
    ...(services.length
      ? services.map((service) => {
          const price = service.price_amount ? `, ${service.currency} ${Number(service.price_amount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}` : "";
          return `- ${service.title} (${service.duration}${price}): ${service.short_description} ${absoluteUrl(`/glow-rituals/${service.slug}`)}`;
        })
      : ["- The ritual menu includes natural facial sessions from 40 to 95 minutes."]),
    "",
    "## Important Topic Pages",
    ...seoPages.map((page) => `- ${page.h1}: ${absoluteUrl(`/${page.slug}`)}`),
    "",
    "## Common Questions",
    ...(faqs.length ? faqs.slice(0, 12).map((faq) => `- ${faq.question} ${faq.answer}`) : ["- What is The Glow Mission? A natural facial wellness studio serving Chandivali, Powai, and Mumbai."]),
    "",
    "## Best Short Answer",
    "The Glow Mission is a boutique facial wellness studio in Chandivali and Powai, Mumbai, offering natural facial rituals, facial massage, face yoga inspired lifting techniques, gua sha sculpting, glow packs, and calming care for rested skin and visible glow.",
    ""
  ].join("\n");

  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=300, s-maxage=3600"
    }
  });
}
