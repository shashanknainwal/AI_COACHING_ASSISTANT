import type { Metadata } from "next";
import { SITE_NAME, SITE_URL, tracksEnabled } from "@/lib/config";
import "./globals.css";

const FDE = {
  title: `${SITE_NAME}: Learn Forward Deployed Engineering`,
  description:
    "The hands-on course for Forward Deployed Engineers: discovery, messy customer data, integrations, Claude-powered agents, evals and production. 100+ lessons and 48 graded Python exercises in your browser.",
};

const TRACKS = {
  title: `${SITE_NAME}: Interview prep for applied AI roles at frontier labs`,
  description:
    "Foundations plus Applied AI Engineer, Applied AI Architect and Forward Deployed Engineer tracks: timed coding drills, graded system design, live mock interviews and real Python in your browser.",
};

export function generateMetadata(): Metadata {
  const { title, description } = tracksEnabled() ? TRACKS : FDE;
  return {
    metadataBase: new URL(SITE_URL),
    title: { default: title, template: `%s · ${SITE_NAME}` },
    description,
    openGraph: { type: "website", url: SITE_URL, siteName: SITE_NAME, title, description },
    twitter: { card: "summary_large_image", title: SITE_NAME, description },
  };
}

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
