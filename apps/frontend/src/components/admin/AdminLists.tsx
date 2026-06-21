"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Download, ExternalLink, Pencil } from "lucide-react";
import { useAdminToast } from "@/components/admin/AdminToasts";
import { adminFetch, apiBaseUrl, authHeaders } from "@/lib/api";

type ApiList<T> = T[] | { results: T[] };

function unwrap<T>(data: ApiList<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

export function useAdminList<T>(path: string) {
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    adminFetch<ApiList<T>>(path)
      .then((data) => setItems(unwrap(data)))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Unable to load data."))
      .finally(() => setLoading(false));
  }, [path]);

  return { items, loading, error };
}

export function AdminTable<T extends { id: number }>({
  path,
  columns,
  title,
  action
}: {
  path: string;
  title: string;
  columns: Array<{ label: string; value: (item: T) => React.ReactNode }>;
  action?: (item: T) => React.ReactNode;
}) {
  const { items, loading, error } = useAdminList<T>(path);

  if (loading) {
    return <div className="border border-champagne/30 bg-ivory p-8 text-sm text-espresso/65">Loading {title.toLowerCase()}...</div>;
  }
  if (error) {
    return <div className="border border-red-200 bg-red-50 p-8 text-sm text-red-700">{error === "AUTH_REQUIRED" ? "Sign in to continue." : error}</div>;
  }

  return (
    <div className="overflow-hidden border border-champagne/30 bg-ivory">
      <div className="border-b border-champagne/25 px-5 py-4">
        <h2 className="font-display text-2xl">{title}</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead className="bg-cream text-xs uppercase tracking-[0.16em] text-espresso/62">
            <tr>
              {columns.map((column) => (
                <th key={column.label} className="px-5 py-4 font-semibold">
                  {column.label}
                </th>
              ))}
              {action && <th className="px-5 py-4 font-semibold">Actions</th>}
            </tr>
          </thead>
          <tbody>
            {!items.length && (
              <tr>
                <td className="px-5 py-8 text-espresso/55" colSpan={columns.length + (action ? 1 : 0)}>
                  No {title.toLowerCase()} found.
                </td>
              </tr>
            )}
            {items.map((item) => (
              <tr key={item.id} className="border-t border-champagne/20">
                {columns.map((column) => (
                  <td key={column.label} className="px-5 py-4 text-espresso/75">
                    {column.value(item)}
                  </td>
                ))}
                {action && <td className="px-5 py-4">{action(item)}</td>}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function EditLink({ href }: { href: string }) {
  return (
    <Link href={href} className="inline-flex items-center gap-2 text-sm font-semibold text-espresso">
      <Pencil size={15} />
      Edit
    </Link>
  );
}

export function ExportLink({ formId, className = "inline-flex items-center gap-2 text-sm font-semibold text-espresso" }: { formId: number; className?: string }) {
  const toast = useAdminToast();

  async function download() {
    const response = await fetch(`${apiBaseUrl()}/admin/campaign-forms/${formId}/responses/export/`, {
      headers: authHeaders()
    });
    if (!response.ok) {
      toast.error("Unable to export campaign responses.");
      return;
    }
    const blob = await response.blob();
    const href = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = filenameFromDisposition(response.headers.get("Content-Disposition")) || `campaign-${formId}-responses.xlsx`;
    anchor.click();
    window.URL.revokeObjectURL(href);
    toast.success("Campaign responses exported.");
  }

  return (
    <button type="button" onClick={download} className={className}>
      <Download size={15} />
      Export
    </button>
  );
}

function filenameFromDisposition(disposition: string | null) {
  if (!disposition) return "";
  const match = disposition.match(/filename="?([^";]+)"?/i);
  return match?.[1] || "";
}

export function PublicLink({ href }: { href: string }) {
  return (
    <Link href={href} className="inline-flex items-center gap-2 text-sm font-semibold text-espresso">
      <ExternalLink size={15} />
      View
    </Link>
  );
}
