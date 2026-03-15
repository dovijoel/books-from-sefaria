"use client";

import { X, BookOpen, Globe, ChevronDown, ChevronUp, Loader2 } from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TextEntry, TextVersion, CommentaryOption } from "@/lib/types";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface TextCardProps {
  entry: TextEntry;
  index: number;
  onChange: (updated: TextEntry) => void;
  onRemove: () => void;
}

export function TextCard({ entry, index, onChange, onRemove }: TextCardProps) {
  const [expanded, setExpanded] = useState(false);

  const displayTitle = entry.link.split("/").pop() ?? entry.link;

  const { data: versions, isLoading: versionsLoading } = useQuery<TextVersion[]>({
    queryKey: ["versions", entry.link],
    queryFn: () => api.getVersions(entry.link),
    enabled: expanded && !!entry.link,
  });

  const { data: dynamicCommentaries, isLoading: commentariesLoading } =
    useQuery<CommentaryOption[]>({
      queryKey: ["commentaries", entry.link],
      queryFn: () => api.getCommentaries(entry.link),
      enabled: expanded && !!entry.link,
    });

  const hebrewVersions = versions?.filter((v) => v.language === "he") ?? [];
  const englishVersions = versions?.filter((v) => v.language === "en") ?? [];

  // Only show commentaries that are actually available for this text (no static fallback).
  const commentaryItems =
    dynamicCommentaries && dynamicCommentaries.length > 0
      ? dynamicCommentaries.map((c) => ({ value: c.title, label: c.heTitle ? `${c.title} (${c.heTitle})` : c.title }))
      : [];

  const toggleCommentary = (value: string) => {
    const current = entry.commentary ?? [];
    const updated = current.includes(value)
      ? current.filter((c) => c !== value)
      : [...current, value];
    onChange({ ...entry, commentary: updated });
  };

  return (
    <Card className="border hover:shadow-sm transition-shadow">
      <CardContent className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className="w-7 h-7 rounded-full bg-sefaria-blue/10 text-sefaria-blue text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
              {index + 1}
            </div>
            <div className="min-w-0">
              <p className="font-medium text-sm truncate">{displayTitle}</p>
              {entry.commentary.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {entry.commentary.map((c) => (
                    <Badge key={c} variant="secondary" className="text-xs">
                      {c}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-1 flex-shrink-0">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              onClick={() => setExpanded((v) => !v)}
              aria-label={expanded ? "Collapse" : "Expand"}
            >
              {expanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 text-destructive hover:text-destructive"
              onClick={onRemove}
              aria-label="Remove text"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Expanded options */}
        {expanded && (
          <div className="mt-4 pt-4 border-t space-y-4">
            {/* Edition / translation pickers */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-xs flex items-center gap-1">
                  <Globe className="h-3 w-3" />
                  Hebrew Edition
                </Label>
                {versionsLoading ? (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Loading editions…
                  </div>
                ) : (
                  <Select
                    value={entry.version_title ?? ""}
                    onValueChange={(val) =>
                      onChange({ ...entry, version_title: val || undefined })
                    }
                  >
                    <SelectTrigger className="h-8 text-sm">
                      <SelectValue placeholder="Default" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Default</SelectItem>
                      {hebrewVersions.map((v) => (
                        <SelectItem key={v.versionTitle} value={v.versionTitle}>
                          {v.versionTitle}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>

              <div className="space-y-1.5">
                <Label className="text-xs flex items-center gap-1">
                  <Globe className="h-3 w-3" />
                  English Translation
                </Label>
                {versionsLoading ? (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Loading translations…
                  </div>
                ) : (
                  <Select
                    value={entry.translation_language ?? ""}
                    onValueChange={(val) =>
                      onChange({ ...entry, translation_language: val || undefined })
                    }
                  >
                    <SelectTrigger className="h-8 text-sm">
                      <SelectValue placeholder="Default" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Default</SelectItem>
                      {englishVersions.map((v) => (
                        <SelectItem key={v.versionTitle} value={v.versionTitle}>
                          {v.versionTitle}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-xs">Range (e.g. 1-5)</Label>
                <Input
                  value={entry.range ?? ""}
                  onChange={(e) => onChange({ ...entry, range: e.target.value })}
                  placeholder="Chapter/verse range"
                  className="h-8 text-sm"
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Daf Range (Talmud)</Label>
                <Input
                  value={entry.dafrange ?? ""}
                  onChange={(e) => onChange({ ...entry, dafrange: e.target.value })}
                  placeholder="e.g. 2a-10b"
                  className="h-8 text-sm"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-xs flex items-center gap-1">
                <BookOpen className="h-3 w-3" />
                Commentaries
                {commentariesLoading && (
                  <Loader2 className="h-3 w-3 animate-spin ml-1" />
                )}
              </Label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {commentaryItems.length > 0 ? (
                  commentaryItems.map(({ value, label }) => (
                    <label
                      key={value}
                      className={cn(
                        "flex items-center gap-2 cursor-pointer rounded-md border px-2 py-1.5 text-xs transition-colors",
                        entry.commentary.includes(value)
                          ? "border-sefaria-blue bg-sefaria-blue/5 text-sefaria-blue"
                          : "border-border hover:border-sefaria-blue/40"
                      )}
                    >
                      <Checkbox
                        checked={entry.commentary.includes(value)}
                        onCheckedChange={() => toggleCommentary(value)}
                        className="h-3 w-3"
                      />
                      <span className="truncate" title={label}>{value}</span>
                    </label>
                  ))
                ) : (
                  !commentariesLoading && (
                    <p className="text-xs text-muted-foreground col-span-full">
                      No commentaries available for this text.
                    </p>
                  )
                )}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
