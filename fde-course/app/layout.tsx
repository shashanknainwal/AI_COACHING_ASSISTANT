import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Forward Deployed Engineering — The Complete Course",
  description:
    "Learn to ship real software inside customer environments: discovery, data, integrations, LLM solutions with Claude, deployment and production support. 10+ hours of hands-on Python exercises in your browser.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
