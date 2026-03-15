import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";
import { Toaster } from "@/components/ui/sonner";
import { NavHeader } from "@/components/nav-header";
import { Github, ExternalLink, Heart } from "lucide-react";

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
      <head>
        {process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID && (
          <script
            defer
            src="/umami/script.js"
            data-website-id={process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID}
            data-host-url="/umami"
          />
        )}
      </head>
      <body className={`${geistSans.variable} antialiased min-h-screen flex flex-col`}>
        <QueryProvider>
          <NavHeader />
          <main className="flex-1">{children}</main>
          <footer className="border-t bg-sefaria-dark text-white/70 py-10">
            <div className="max-w-6xl mx-auto px-4 text-sm">
              {/* Top row */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
                <div className="flex items-center gap-2">
                  <span className="text-sefaria-gold font-semibold">Sefaria Book Creator</span>
                  <span>·</span>
                  <span>Beautifully typeset Jewish texts</span>
                </div>
                <div className="flex items-center gap-4">
                  <a
                    href="https://github.com/dovijoel/books-from-sefaria"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 text-white/70 hover:text-sefaria-gold transition-colors"
                  >
                    <Github className="h-4 w-4" />
                    GitHub
                  </a>
                  <a
                    href="https://github.com/dovijoel/books-from-sefaria/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 text-white/70 hover:text-sefaria-gold transition-colors"
                  >
                    Report an Issue
                  </a>
                </div>
              </div>

              {/* Divider */}
              <div className="border-t border-white/10 pt-5 space-y-3 text-xs text-white/50">
                {/* Sefaria content attribution */}
                <p>
                  All Jewish text content is sourced from{" "}
                  <a
                    href="https://www.sefaria.org"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sefaria-gold hover:underline"
                  >
                    Sefaria
                  </a>{" "}
                  and is available under a{" "}
                  <a
                    href="https://creativecommons.org/licenses/by-nc/4.0/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-white/70 hover:underline"
                  >
                    Creative Commons BY-NC 4.0
                  </a>{" "}
                  license. Please see{" "}
                  <a
                    href="https://www.sefaria.org/terms"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-white/70 hover:underline"
                  >
                    Sefaria&apos;s Terms of Use
                  </a>{" "}
                  for details.
                </p>

                {/* Original project attribution */}
                <p className="flex flex-wrap items-center gap-1">
                  <span>Built with</span>
                  <Heart className="h-3 w-3 text-red-400 inline" />
                  <span>· Originally forked from</span>
                  <a
                    href="https://github.com/nkasimer/books-from-sefaria"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-white/70 hover:underline inline-flex items-center gap-1"
                  >
                    nkasimer/books-from-sefaria
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </p>

                {/* Contribute callout */}
                <p>
                  This project is open source — contributions, bug reports, and feature requests are welcome on{" "}
                  <a
                    href="https://github.com/dovijoel/books-from-sefaria"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sefaria-gold hover:underline"
                  >
                    GitHub
                  </a>
                  .
                </p>
              </div>
            </div>
          </footer>
          <Toaster richColors position="top-right" />
        </QueryProvider>
      </body>
    </html>
  );
}
