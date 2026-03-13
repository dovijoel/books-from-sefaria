"use client";

import { useRouter } from "next/navigation";
import { CheckCircle2, Clock, Loader2, XCircle, Download, RotateCcw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Job } from "@/lib/types";
import { cn } from "@/lib/utils";

const STATUS_CONFIG = {
  pending: {
    icon: Clock,
    color: "text-yellow-500",
    bg: "bg-yellow-50 border-yellow-200",
    label: "Pending",
    progress: 10,
  },
  running: {
    icon: Loader2,
    color: "text-blue-500",
    bg: "bg-blue-50 border-blue-200",
    label: "Running",
    progress: 60,
  },
  completed: {
    icon: CheckCircle2,
    color: "text-green-600",
    bg: "bg-green-50 border-green-200",
    label: "Completed",
    progress: 100,
  },
  failed: {
    icon: XCircle,
    color: "text-destructive",
    bg: "bg-destructive/5 border-destructive/20",
    label: "Failed",
    progress: 100,
  },
};

interface JobStatusCardProps {
  job: Job;
  compact?: boolean;
}

export function JobStatusCard({ job, compact = false }: JobStatusCardProps) {
  const router = useRouter();
  const cfg = STATUS_CONFIG[job.status];
  const Icon = cfg.icon;
  const isSpinning = job.status === "running";

  return (
    <Card className={cn("border transition-shadow", cfg.bg)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon
              className={cn("h-5 w-5", cfg.color, isSpinning && "animate-spin")}
            />
            <CardTitle className="text-base">
              {job.config?.name ?? `Job ${job.id.slice(0, 8)}`}
            </CardTitle>
          </div>
          <Badge
            variant="outline"
            className={cn("text-xs capitalize", cfg.color)}
          >
            {cfg.label}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <Progress value={cfg.progress} className="h-1.5" />

        {!compact && (
          <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
            <div>
              <span className="font-medium text-foreground">Job ID</span>
              <p className="font-mono truncate">{job.id.slice(0, 16)}…</p>
            </div>
            <div>
              <span className="font-medium text-foreground">Started</span>
              <p>{new Date(job.createdAt).toLocaleString()}</p>
            </div>
            {job.completedAt && (
              <div>
                <span className="font-medium text-foreground">Completed</span>
                <p>{new Date(job.completedAt).toLocaleString()}</p>
              </div>
            )}
            {job.config?.texts?.length !== undefined && (
              <div>
                <span className="font-medium text-foreground">Texts</span>
                <p>{job.config.texts.length}</p>
              </div>
            )}
          </div>
        )}

        {job.error && (
          <div className="rounded-md bg-destructive/10 border border-destructive/20 px-3 py-2 text-xs text-destructive">
            {job.error}
          </div>
        )}

        <div className="flex gap-2 pt-1">
          {job.status === "completed" && job.pdfUrl && (
            <a
              href={job.pdfUrl}
              download
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium h-9 px-3 bg-sefaria-blue hover:bg-sefaria-blue-hover text-white transition-colors"
            >
              <Download className="h-4 w-4 mr-1.5" />
              Download PDF
            </a>
          )}
          {!compact && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => router.push("/builder")}
            >
              <RotateCcw className="h-4 w-4 mr-1.5" />
              New Book
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
