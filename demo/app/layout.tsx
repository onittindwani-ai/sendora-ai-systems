import type { Metadata } from "next";
import type { ReactNode } from "react";
import { themeInitScript } from "@sendora/ui-kit";
import "@sendora/ui-kit/styles.css";

export const metadata: Metadata = { title: "UI kit demo", description: "Proof that the shared UI kit renders." };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-accent="clay" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
