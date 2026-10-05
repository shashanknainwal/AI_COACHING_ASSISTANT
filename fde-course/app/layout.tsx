import type { Metadata } from "next";
import { SITE_NAME, SITE_URL } from "@/lib/config";
import "./globals.css";

const description =
  "The hands-on course for Forward Deployed Engineers: discovery, messy customer data, integrations, Claude-powered agents, evals and production. 100+ lessons and 48 graded Python exercises in your browser.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: `${SITE_NAME}: Learn Forward Deployed Engineering`, template: `%s · ${SITE_NAME}` },
  description,
  openGraph: { type: "website", url: SITE_URL, siteName: SITE_NAME, title: `${SITE_NAME}: Learn Forward Deployed Engineering`, description },
  twitter: { card: "summary_large_image", title: SITE_NAME, description },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
        />
      </head>
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
