import { PublicCmsPage } from "@/components/public/PublicCmsPage";
import { cmsPageMetadata } from "@/lib/metadata";

export const dynamic = "force-dynamic";

export function generateMetadata() {
  return cmsPageMetadata("glow-rituals");
}

export default function GlowRitualsPage() {
  return <PublicCmsPage slug="glow-rituals" />;
}
