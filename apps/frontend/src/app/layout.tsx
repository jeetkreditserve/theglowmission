import "./globals.css";
import type { Metadata } from "next";
import { absoluteUrl, defaultSeoDescription, defaultSocialImage, siteName, siteUrl } from "@/lib/site";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl()),
  title: {
    default: siteName,
    template: "%s | The Glow Mission"
  },
  description: defaultSeoDescription,
  alternates: {
    canonical: siteUrl()
  },
  openGraph: {
    title: siteName,
    description: defaultSeoDescription,
    url: siteUrl(),
    siteName,
    type: "website",
    locale: "en_IN",
    images: [
      {
        url: absoluteUrl(defaultSocialImage),
        width: 1254,
        height: 1254,
        alt: "The Glow Mission natural facial ritual"
      }
    ]
  },
  twitter: {
    card: "summary_large_image",
    title: siteName,
    description: defaultSeoDescription,
    images: [absoluteUrl(defaultSocialImage)]
  },
  icons: {
    icon: [{ url: "/favicon.ico", sizes: "any" }],
    shortcut: ["/favicon.ico"],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }]
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
