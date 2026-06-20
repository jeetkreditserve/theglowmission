import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Glow Mission",
  description: "Glow, the natural way."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

