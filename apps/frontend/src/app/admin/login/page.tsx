import { LoginForm } from "@/components/admin/LoginForm";

export default function AdminLoginPage() {
  return (
    <main className="texture-bg flex min-h-screen items-center justify-center px-5 py-10">
      <section className="w-full max-w-md border border-champagne/30 bg-cream p-8 spa-shadow">
        <p className="display-title text-sm text-champagne">The Glow Mission CMS</p>
        <h1 className="mt-4 font-display text-4xl text-espresso">Sign in</h1>
        <p className="mt-3 text-sm leading-6 text-espresso/65">Manage public pages, services, gallery assets, FAQs, campaigns, and responses.</p>
        <div className="mt-8">
          <LoginForm />
        </div>
      </section>
    </main>
  );
}

