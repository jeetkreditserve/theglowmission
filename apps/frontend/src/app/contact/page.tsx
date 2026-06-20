import { PublicCmsPage } from "@/components/public/PublicCmsPage";
import { cmsPageMetadata } from "@/lib/metadata";

export const dynamic = "force-dynamic";

export function generateMetadata() {
  return cmsPageMetadata("contact");
}

export default function ContactPage() {
  return <PublicCmsPage slug="contact" />;
}
