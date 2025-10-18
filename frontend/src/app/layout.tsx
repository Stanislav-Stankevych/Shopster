import "@/app/globals.css";

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { PropsWithChildren } from "react";

import { LayoutProviders } from "@/components/LayoutProviders";
import { defaultMetadata } from "@/lib/seo";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = defaultMetadata;

export default function RootLayout({ children }: PropsWithChildren) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <LayoutProviders>{children}</LayoutProviders>
      </body>
    </html>
  );
}
