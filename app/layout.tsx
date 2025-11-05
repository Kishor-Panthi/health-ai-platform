import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { CommandPaletteProvider } from "@/components/shared/CommandPaletteProvider";

export const metadata: Metadata = {
  title: "HealthCare PM - Practice Management System",
  description: "Comprehensive healthcare practice management system for small to mid-size medical practices",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <Providers>
          <CommandPaletteProvider>{children}</CommandPaletteProvider>
        </Providers>
      </body>
    </html>
  );
}
