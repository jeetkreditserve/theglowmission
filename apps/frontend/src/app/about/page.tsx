import { PublicCmsPage } from "@/components/public/PublicCmsPage";
import { cmsPageMetadata } from "@/lib/metadata";

export const dynamic = "force-dynamic";

export function generateMetadata() {
  return cmsPageMetadata("about");
}

export default function AboutPage() {
  return <PublicCmsPage slug="about" />;
}
