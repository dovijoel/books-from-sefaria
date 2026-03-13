"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, BookMarked, Cpu } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { href: "/builder", label: "Builder", icon: BookOpen },
  { href: "/configs", label: "Saved Configs", icon: BookMarked },
];

export function NavHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-sefaria-dark/95 backdrop-blur text-white">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-md bg-sefaria-gold flex items-center justify-center">
            <BookOpen className="h-4 w-4 text-sefaria-dark" />
          </div>
          <span className="font-bold text-lg tracking-tight group-hover:text-sefaria-gold transition-colors">
            Sefaria Book Creator
          </span>
        </Link>

        {/* Nav links */}
        <nav className="hidden sm:flex items-center gap-1">
          {NAV_LINKS.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                pathname === href || pathname.startsWith(href + "/")
                  ? "bg-sefaria-gold/20 text-sefaria-gold"
                  : "text-white/70 hover:text-white hover:bg-white/10"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
          <Link
            href="/jobs"
            className={cn(
              "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors",
              pathname.startsWith("/jobs")
                ? "bg-sefaria-gold/20 text-sefaria-gold"
                : "text-white/70 hover:text-white hover:bg-white/10"
            )}
          >
            <Cpu className="h-4 w-4" />
            Jobs
          </Link>
        </nav>
      </div>
    </header>
  );
}
