"use client";

import { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Loader2, BookOpen } from "lucide-react";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { SefariaTextSearchResult } from "@/lib/types";

interface TextSearchProps {
  onSelect: (result: SefariaTextSearchResult) => void;
  placeholder?: string;
}

export function TextSearch({
  onSelect,
  placeholder = "Search Sefaria texts…",
}: TextSearchProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Debounce input
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 350);
    return () => clearTimeout(timer);
  }, [query]);

  const { data, isLoading } = useQuery({
    queryKey: ["sefaria-search", debouncedQuery],
    queryFn: () => api.searchTexts(debouncedQuery),
    enabled: debouncedQuery.trim().length > 2,
    staleTime: 5 * 60 * 1000,
  });

  // Close dropdown on outside click
  useEffect(() => {
    const handleOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  const results = data ?? [];

  return (
    <div ref={wrapperRef} className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="pl-9 pr-9"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
        )}
      </div>

      {isOpen && query.length > 2 && (
        <div className="absolute z-50 mt-1 w-full rounded-lg border bg-popover shadow-lg overflow-hidden">
          {results.length === 0 && !isLoading ? (
            <div className="py-6 text-center text-sm text-muted-foreground">
              No results found for &ldquo;{query}&rdquo;
            </div>
          ) : (
            <ul className="max-h-72 overflow-y-auto py-1">
              {results.map((result) => (
                <li
                  key={result.ref}
                  className="flex items-start gap-3 cursor-pointer px-3 py-2.5 hover:bg-accent transition-colors"
                  onMouseDown={(e) => {
                    e.preventDefault(); // prevent blur before click
                    onSelect(result);
                    setQuery("");
                    setIsOpen(false);
                  }}
                >
                  <BookOpen className="h-4 w-4 mt-0.5 text-sefaria-blue flex-shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{result.title}</p>
                    <p className="text-xs text-muted-foreground truncate">{result.ref}</p>
                    {result.heTitle && (
                      <p dir="rtl" className="text-xs text-muted-foreground mt-0.5">
                        {result.heTitle}
                      </p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
