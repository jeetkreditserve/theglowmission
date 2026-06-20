"use client";

import { useParams } from "next/navigation";
import { AdminShell } from "@/components/admin/AdminShell";
import { AdminTable } from "@/components/admin/AdminLists";

type CampaignField = { id: number; label: string; key: string; field_type: string; required: boolean; ordering: number; active: boolean };

export default function CampaignBuilderPage() {
  const params = useParams<{ id: string }>();
  return (
    <AdminShell title="Campaign Builder">
      <AdminTable<CampaignField>
        path={`/admin/campaign-fields/?form=${params.id}`}
        title="Fields"
        columns={[
          { label: "Label", value: (item) => item.label },
          { label: "Key", value: (item) => item.key },
          { label: "Type", value: (item) => item.field_type },
          { label: "Required", value: (item) => (item.required ? "Yes" : "No") },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") }
        ]}
      />
    </AdminShell>
  );
}

