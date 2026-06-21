"use client";

import { useParams } from "next/navigation";
import { AdminShell } from "@/components/admin/AdminShell";
import { AdminResourceManager } from "@/components/admin/AdminResourceManager";

type CampaignField = {
  id: number;
  form: number;
  label: string;
  key: string;
  field_type: string;
  placeholder: string;
  help_text: string;
  required: boolean;
  options: string[];
  validation: Record<string, unknown>;
  ordering: number;
  active: boolean;
};

export default function CampaignBuilderPage() {
  const params = useParams<{ id: string }>();
  const formId = Number(params.id);

  return (
    <AdminShell title="Campaign Builder">
      <AdminResourceManager<CampaignField>
        path="/admin/campaign-fields/"
        queryKey={`form=${formId}`}
        title="Form fields"
        itemLabel="field"
        createLabel="New field"
        defaults={{
          form: formId,
          label: "",
          key: "",
          field_type: "text",
          placeholder: "",
          help_text: "",
          required: false,
          options: [],
          validation: {},
          ordering: 0,
          active: true
        }}
        columns={[
          { label: "Label", value: (item) => item.label },
          { label: "Key", value: (item) => item.key },
          { label: "Type", value: (item) => item.field_type },
          { label: "Required", value: (item) => (item.required ? "Yes" : "No") },
          { label: "Active", value: (item) => (item.active ? "Yes" : "No") }
        ]}
        fields={[
          { name: "label", label: "Label", required: true },
          { name: "key", label: "Key", help: "Cannot be changed after responses exist." },
          {
            name: "field_type",
            label: "Field type",
            type: "select",
            required: true,
            options: [
              { label: "Text", value: "text" },
              { label: "Textarea", value: "textarea" },
              { label: "Email", value: "email" },
              { label: "Phone", value: "phone" },
              { label: "Select", value: "select" },
              { label: "Checkbox", value: "checkbox" },
              { label: "Radio", value: "radio" },
              { label: "Date", value: "date" },
              { label: "Number", value: "number" }
            ]
          },
          { name: "placeholder", label: "Placeholder" },
          { name: "help_text", label: "Help text", span: "full" },
          { name: "options", label: "Options", type: "jsonList", span: "full", help: "One option per line for select/radio fields." },
          { name: "validation", label: "Validation JSON", type: "json", span: "full" },
          { name: "required", label: "Required", type: "checkbox" },
          { name: "active", label: "Active", type: "checkbox" },
          { name: "ordering", label: "Order", type: "number" }
        ]}
        transformPayload={(payload) => ({ ...payload, form: formId })}
      />
    </AdminShell>
  );
}
