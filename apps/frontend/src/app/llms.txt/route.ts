import { getServices } from "@/lib/api";
import { absoluteUrl } from "@/lib/site";

export const dynamic = "force-dynamic";

export async function GET() {
  const services = await getServices().catch(() => []);
  const serviceLines = services.map((service) => `- ${service.title}: ${absoluteUrl(`/glow-rituals/${service.slug}`)}`);
  const body = [
    "# The Glow Mission",
    "",
    "The Glow Mission is a boutique facial wellness studio serving Chandivali, Powai, and Mumbai, India.",
    "It offers natural facial rituals, facial massage, face yoga inspired lifting techniques, gua sha sculpting, glow packs, calming breathwork, warm steam, cooling therapy, and consultation-led beauty care.",
    "The brand story is rooted in a mother's cosmetology wisdom, natural ingredients, gentle hands, visible glow, restful touch, and confidence in one's own skin.",
    "",
    "## Canonical pages",
    `- Home: ${absoluteUrl("/")}`,
    `- What is The Glow Mission: ${absoluteUrl("/what-is-the-glow-mission")}`,
    `- Glow rituals: ${absoluteUrl("/glow-rituals")}`,
    `- About: ${absoluteUrl("/about")}`,
    `- Contact: ${absoluteUrl("/contact")}`,
    "",
    "## Rituals",
    ...(serviceLines.length ? serviceLines : ["- Ritual menu: natural facial sessions from 50 to 90 minutes"]),
    "",
    `Full AI-readable guide: ${absoluteUrl("/llms-full.txt")}`,
    ""
  ].join("\n");

  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, max-age=300, s-maxage=3600"
    }
  });
}
