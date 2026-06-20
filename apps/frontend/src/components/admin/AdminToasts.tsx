"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { CheckCircle2, XCircle } from "lucide-react";

type ToastTone = "success" | "error";
type Toast = { id: number; tone: ToastTone; message: string };
type ToastContextValue = {
  success: (message: string) => void;
  error: (message: string) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

export function AdminToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = useCallback((tone: ToastTone, message: string) => {
    const id = Date.now() + Math.random();
    setToasts((current) => [...current, { id, tone, message }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, 5200);
  }, []);

  const value = useMemo(
    () => ({
      success: (message: string) => push("success", message),
      error: (message: string) => push("error", message)
    }),
    [push]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-5 top-5 z-[90] grid w-[min(92vw,420px)] gap-3">
        {toasts.map((toast) => {
          const Icon = toast.tone === "success" ? CheckCircle2 : XCircle;
          return (
            <div
              key={toast.id}
              role="status"
              className={`flex items-start gap-3 border px-4 py-3 text-sm shadow-[0_18px_55px_rgba(37,29,24,0.16)] ${
                toast.tone === "success" ? "border-champagne/40 bg-ivory text-espresso" : "border-red-200 bg-red-50 text-red-800"
              }`}
            >
              <Icon size={18} className="mt-0.5 shrink-0" />
              <span className="leading-6">{toast.message}</span>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useAdminToast() {
  const context = useContext(ToastContext);
  if (!context) {
    return {
      success: () => undefined,
      error: () => undefined
    };
  }
  return context;
}
