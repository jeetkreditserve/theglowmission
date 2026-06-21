"use client";

import Link from "next/link";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { FileText, GalleryHorizontalEnd, HelpCircle, Images, Inbox, LayoutDashboard, Link2, LogOut, MessageSquareQuote, Palette, Sparkles, SquarePen, Tags, Users, View } from "lucide-react";
import { AdminToastProvider } from "@/components/admin/AdminToasts";

const navItems = [
  { label: "Overview", href: "/admin", icon: LayoutDashboard },
  { label: "Theme", href: "/admin/theme", icon: Palette },
  { label: "Navigation", href: "/admin/navigation", icon: Link2 },
  { label: "Hero", href: "/admin/hero", icon: View },
  { label: "Pages", href: "/admin/pages", icon: FileText },
  { label: "Glow Rituals", href: "/admin/glow-rituals", icon: Sparkles },
  { label: "Gallery", href: "/admin/gallery", icon: GalleryHorizontalEnd },
  { label: "Media", href: "/admin/media", icon: Images },
  { label: "FAQs", href: "/admin/faqs", icon: HelpCircle },
  { label: "Testimonials", href: "/admin/testimonials", icon: MessageSquareQuote },
  { label: "Contacts", href: "/admin/contacts", icon: Users },
  { label: "Contact Statuses", href: "/admin/contact-statuses", icon: Tags },
  { label: "Campaigns", href: "/admin/campaigns", icon: SquarePen },
  { label: "Responses", href: "/admin/campaign-responses", icon: Inbox }
];

export function AdminShell({ title, children }: { title: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!window.localStorage.getItem("glow_admin_token")) {
      router.replace("/admin/login");
    }
  }, [router]);

  function logout() {
    window.localStorage.removeItem("glow_admin_token");
    router.push("/admin/login");
  }

  return (
    <AdminToastProvider>
      <div className="min-h-screen bg-[#f5eee5] text-espresso">
        <div className="grid min-h-screen lg:grid-cols-[260px_1fr]">
          <aside className="border-r border-champagne/20 bg-[#211915] px-5 py-6 text-ivory">
            <Link href="/admin" className="block">
              <p className="display-title text-lg leading-7">The Glow Mission</p>
              <p className="mt-2 text-xs uppercase tracking-[0.18em] text-champagne">CMS</p>
            </Link>
            <nav className="mt-10 space-y-1">
              {navItems.map((item) => {
                const active = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-3 text-sm transition ${active ? "bg-white/12 text-white" : "text-ivory/72 hover:bg-white/8 hover:text-white"}`}
                  >
                    <Icon size={17} strokeWidth={1.8} />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
            <button onClick={logout} className="mt-10 flex w-full items-center gap-3 px-3 py-3 text-left text-sm text-ivory/72 transition hover:bg-white/8 hover:text-white">
              <LogOut size={17} strokeWidth={1.8} />
              Logout
            </button>
          </aside>
          <section className="min-w-0">
            <header className="border-b border-champagne/30 bg-ivory/85 px-5 py-6 backdrop-blur lg:px-8">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-champagne">Admin</p>
              <h1 className="mt-2 font-display text-4xl text-espresso">{title}</h1>
            </header>
            <main className="px-5 py-8 lg:px-8">{children}</main>
          </section>
        </div>
      </div>
    </AdminToastProvider>
  );
}
