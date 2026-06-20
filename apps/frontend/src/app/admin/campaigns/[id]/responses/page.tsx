"use client";

import { useParams } from "next/navigation";
import { AdminShell } from "@/components/admin/AdminShell";
import { AdminTable, ExportLink } from "@/components/admin/AdminLists";

type ResponseItem = { id: number; submitted_at: string; response_data: Record<string, string>; metadata: Record<string, string> };

export default function CampaignResponsesPage() {
  const params = useParams<{ id: string }>();
  const formId = Number(params.id);
  return (
    <AdminShell title="Campaign Responses">
      <div className="mb-5">
        <ExportLink formId={formId} />
      </div>
      <AdminTable<ResponseItem>
        path={`/admin/campaign-forms/${formId}/responses/`}
        title="Responses"
        columns={[
          { label: "ID", value: (item) => item.id },
          { label: "Submitted", value: (item) => new Date(item.submitted_at).toLocaleString() },
          { label: "Response", value: (item) => JSON.stringify(item.response_data) },
          { label: "User agent", value: (item) => item.metadata?.user_agent || "" }
        ]}
      />
    </AdminShell>
  );
}

