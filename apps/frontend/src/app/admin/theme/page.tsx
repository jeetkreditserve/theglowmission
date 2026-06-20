import { AdminShell } from "@/components/admin/AdminShell";
import { ThemeEditor } from "@/components/admin/ThemeEditor";

export default function AdminThemePage() {
  return (
    <AdminShell title="Theme">
      <ThemeEditor />
    </AdminShell>
  );
}

