"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { JobStatusCard } from "@/components/job-status-card";
import { api } from "@/lib/api";
import { Job } from "@/lib/types";

export default function JobPage() {
  const params = useParams();
  const jobId = params.id as string;

  const { data: job, isLoading, isError, error } = useQuery<Job>({
    queryKey: ["job", jobId],
    queryFn: () => api.getJob(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "pending" || status === "running" ? 3000 : false;
    },
    enabled: Boolean(jobId),
  });

  return (
    <div className="max-w-2xl mx-auto py-12 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Job Status</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Job ID:{" "}
          <span className="font-mono">{jobId}</span>
        </p>
      </div>

      {isLoading && (
        <Card>
          <CardContent className="p-6 space-y-4">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-2 w-full" />
            <Skeleton className="h-4 w-32" />
          </CardContent>
        </Card>
      )}

      {isError && (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardContent className="p-6 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <p className="font-medium text-destructive">Could not load job</p>
              <p className="text-sm text-muted-foreground">
                {(error as Error)?.message ?? "Unknown error"}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-2"
                onClick={() => window.location.reload()}
              >
                Try again
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {job && <JobStatusCard job={job} />}

      {job?.status === "pending" || job?.status === "running" ? (
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Checking for updates every 3 seconds…
        </div>
      ) : null}
    </div>
  );
}
