"use client";

import Link from "next/link";
import { Eye, FileText, SquarePen } from "lucide-react";
import { ExportLink } from "@/components/admin/AdminLists";

export type CampaignActionItem = {
  id: number;
  slug: string;
};

export function CampaignActions({ campaign, compact = false }: { campaign: CampaignActionItem; compact?: boolean }) {
  const linkClass = compact ? "admin-icon-link px-2 py-1.5" : "admin-icon-link";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Link href={`/admin/campaigns/${campaign.id}/builder`} className={linkClass}>
        <SquarePen size={15} />
        Builder
      </Link>
      <Link href={`/admin/campaigns/${campaign.id}/responses`} className={linkClass}>
        <FileText size={15} />
        Responses
      </Link>
      <Link href={`/campaigns/${campaign.slug}`} target="_blank" className={linkClass}>
        <Eye size={15} />
        Preview
      </Link>
      <ExportLink formId={campaign.id} className={linkClass} />
    </div>
  );
}
