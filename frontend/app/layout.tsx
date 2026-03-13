import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";
import { Toaster } from "@/components/ui/sonner";
import { NavHeader } from "@/components/nav-header";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sefaria Book Creator",
  description:
    "Turn Jewish texts into beautiful, professionally typeset books — powered by Sefaria.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} antialiased min-h-screen flex flex-col`}>
        <QueryProvider>
          <NavHeader />
          <main className="flex-1">{children}</main>
          <footer className="border-t bg-sefaria-dark text-white/70 py-8">
            <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-sefaria-gold font-semibold">Sefaria Book Creator</span>
                <span>·</span>
                <span>Beautifully typeset Jewish texts</span>
              </div>
              <div className="flex items-center gap-1">
                <span>Powered by</span>
                <a
                  href="https://www.sefaria.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sefaria-gold hover:underline font-medium"
                >
                  Sefaria
                </a>
              </div>
            </div>
          </footer>
          <Toaster richColors position="top-right" />
        </QueryProvider>
      </body>
    </html>
  );
}
