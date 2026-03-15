"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, ArrowRight, Clock, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function JobsPage() {
  const router = useRouter();
  const [jobId, setJobId] = useState("");

  const handleLookup = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = jobId.trim();
    if (trimmed) {
      router.push(`/jobs/${trimmed}`);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-12 px-4 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Job Status</h1>
        <p className="text-muted-foreground">
          Look up the status of a PDF generation job by entering its ID below.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Search className="h-5 w-5" />
            Look Up a Job
          </CardTitle>
          <CardDescription>
            When you generate a PDF, you receive a job ID. Paste it here to
            check its progress.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLookup} className="flex gap-2">
            <Input
              placeholder="e.g. 3f8a1c2d-9b4e-4f6a-..."
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              className="font-mono text-sm"
            />
            <Button
              type="submit"
              disabled={!jobId.trim()}
              className="bg-sefaria-blue hover:bg-sefaria-blue-hover text-white shrink-0"
            >
              <ArrowRight className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="text-center space-y-4 pt-4">
        <div className="flex items-center gap-3 justify-center text-muted-foreground text-sm">
          <div className="flex items-center gap-1.5">
            <Clock className="h-4 w-4" />
            <span>Jobs auto-refresh while in progress</span>
          </div>
          <span className="text-muted-foreground/40">|</span>
          <div className="flex items-center gap-1.5">
            <FileText className="h-4 w-4" />
            <span>PDFs are available after completion</span>
          </div>
        </div>

        <Button
          variant="outline"
          onClick={() => router.push("/builder")}
          className="mt-2"
        >
          Go to Builder
          <ArrowRight className="ml-1.5 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
