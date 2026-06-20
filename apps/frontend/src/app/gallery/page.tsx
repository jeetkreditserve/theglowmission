import { PublicCmsPage } from "@/components/public/PublicCmsPage";
import { cmsPageMetadata } from "@/lib/metadata";

export const dynamic = "force-dynamic";

export function generateMetadata() {
  return cmsPageMetadata("gallery");
}

export default function GalleryPage() {
  return <PublicCmsPage slug="gallery" />;
}
