"use client";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Loader2, Trash2, BookOpen, Plus, AlertCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { api } from "@/lib/api";
import { BookConfigListItem } from "@/lib/types";
import { useState } from "react";

export default function ConfigsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const { data: configs, isLoading, isError } = useQuery<BookConfigListItem[]>({
    queryKey: ["configs"],
    queryFn: api.getConfigs,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteConfig(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configs"] });
      toast.success("Configuration deleted");
      setDeletingId(null);
    },
    onError: (err: Error) => {
      toast.error(err.message ?? "Failed to delete");
    },
  });

  const loadIntoBuilder = (config: BookConfigListItem) => {
    sessionStorage.setItem("builderConfig", JSON.stringify(config));
    toast.success("Configuration loaded into builder");
    router.push("/builder");
  };

  return (
    <div className="max-w-5xl mx-auto py-10 px-4">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Saved Configurations</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Reuse your book settings without starting from scratch.
          </p>
        </div>
        <Button
          onClick={() => router.push("/builder")}
          className="bg-sefaria-blue hover:bg-sefaria-blue-hover text-white"
        >
          <Plus className="h-4 w-4 mr-1.5" />
          New Book
        </Button>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-3">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-3 w-24 mt-1" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-3 w-full mb-2" />
                <Skeleton className="h-3 w-2/3" />
              </CardContent>
              <CardFooter className="gap-2">
                <Skeleton className="h-8 w-24" />
                <Skeleton className="h-8 w-16" />
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {isError && (
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-3">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <p className="font-medium">Failed to load configurations</p>
          <Button variant="outline" onClick={() => queryClient.invalidateQueries({ queryKey: ["configs"] })}>
            Try again
          </Button>
        </div>
      )}

      {configs && configs.length === 0 && (
        <div className="flex flex-col items-center justify-center py-24 text-center space-y-4">
          <BookOpen className="h-12 w-12 text-muted-foreground/40" />
          <div>
            <p className="font-medium text-lg">No saved configurations</p>
            <p className="text-muted-foreground text-sm mt-1">
              Create a book in the builder and save your settings for reuse.
            </p>
          </div>
          <Button
            onClick={() => router.push("/builder")}
            className="bg-sefaria-blue hover:bg-sefaria-blue-hover text-white"
          >
            Open Builder
          </Button>
        </div>
      )}

      {configs && configs.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {configs.map((config) => (
            <Card key={config.id} className="flex flex-col hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="text-base leading-snug">
                  {config.name ?? "Untitled"}
                </CardTitle>
                {config.createdAt && (
                  <CardDescription className="flex items-center gap-1 text-[11px]">
                    <Clock className="h-3 w-3" />
                    {new Date(config.createdAt).toLocaleDateString()}
                  </CardDescription>
                )}
              </CardHeader>

              <CardContent className="text-sm text-muted-foreground flex-1">
                {config.description && (
                  <p className="text-xs line-clamp-2">{config.description}</p>
                )}
              </CardContent>

              <CardFooter className="flex gap-2 pt-3 border-t">
                <Button
                  size="sm"
                  className="flex-1 bg-sefaria-blue hover:bg-sefaria-blue-hover text-white"
                  onClick={() => loadIntoBuilder(config)}
                >
                  Load
                </Button>

                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setDeletingId(config.id)}
                  className="text-destructive hover:bg-destructive/10 border-destructive/30"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>

                <Dialog
                  open={deletingId === config.id}
                  onOpenChange={(open) => !open && setDeletingId(null)}
                >
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Delete configuration?</DialogTitle>
                      <DialogDescription>
                        &ldquo;{config.name ?? "Untitled"}&rdquo; will be permanently deleted.
                        This cannot be undone.
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setDeletingId(null)}>
                        Cancel
                      </Button>
                      <Button
                        variant="destructive"
                        disabled={deleteMutation.isPending}
                        onClick={() => deleteMutation.mutate(config.id)}
                      >
                        {deleteMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          "Delete"
                        )}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}