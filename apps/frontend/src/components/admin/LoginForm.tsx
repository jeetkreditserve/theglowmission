"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiBaseUrl } from "@/lib/api";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const response = await fetch(`${apiBaseUrl()}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    setLoading(false);
    if (!response.ok) {
      setError("Invalid email or password.");
      return;
    }
    const data = (await response.json()) as { token: string };
    window.localStorage.setItem("glow_admin_token", data.token);
    router.push("/admin");
  }

  return (
    <form onSubmit={submit} className="space-y-5">
      <label className="block">
        <span className="text-sm font-semibold uppercase tracking-[0.16em] text-espresso/70">Email</span>
        <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required className="mt-3 w-full border border-champagne/35 bg-ivory px-4 py-4 outline-none focus:border-champagne" />
      </label>
      <label className="block">
        <span className="text-sm font-semibold uppercase tracking-[0.16em] text-espresso/70">Password</span>
        <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required className="mt-3 w-full border border-champagne/35 bg-ivory px-4 py-4 outline-none focus:border-champagne" />
      </label>
      <button disabled={loading} className="w-full bg-champagne px-7 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-espresso disabled:opacity-60">
        {loading ? "Signing in..." : "Sign in"}
      </button>
      {error && <p className="text-sm text-red-700">{error}</p>}
    </form>
  );
}

