"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Loader2, CheckCircle2, BookOpen, Settings, Palette, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { TextSearch } from "@/components/text-search";
import { TextCard } from "@/components/text-card";
import { BookSettingsForm } from "@/components/book-settings-form";
import { api } from "@/lib/api";
import { TextEntry, BookFormatSettings, BookConfig, DEFAULT_FORMAT, SefariaTextSearchResult } from "@/lib/types";
import { cn } from "@/lib/utils";

const STEPS = [
  { id: "texts", label: "Choose Texts", icon: BookOpen },
  { id: "format", label: "Layout & Type", icon: Settings },
  { id: "cover", label: "Cover Design", icon: Palette },
  { id: "review", label: "Review", icon: Eye },
];

const variants = {
  enter: (dir: number) => ({ x: dir > 0 ? 60 : -60, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (dir: number) => ({ x: dir < 0 ? 60 : -60, opacity: 0 }),
};

export default function BuilderPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [dir, setDir] = useState(1);
  const [bookName, setBookName] = useState("My Sefaria Book");
  const [texts, setTexts] = useState<TextEntry[]>([]);
  const [format, setFormat] = useState<BookFormatSettings>(DEFAULT_FORMAT);

  const go = (next: number) => {
    setDir(next > step ? 1 : -1);
    setStep(next);
  };

  const addText = (result: SefariaTextSearchResult) => {
    if (texts.find((t) => t.link === result.ref)) {
      toast.info("Text already added");
      return;
    }
    setTexts((prev) => [
      ...prev,
      { link: result.ref, commentary: [], translation: "", range: "" },
    ]);
  };

  const removeText = (link: string) =>
    setTexts((prev) => prev.filter((t) => t.link !== link));

  const updateText = (link: string, updated: TextEntry) =>
    setTexts((prev) =>
      prev.map((t) => (t.link === link ? updated : t))
    );

  const createJobMutation = useMutation({
    mutationFn: (config: BookConfig) => api.createJob(config),
    onSuccess: (data) => {
      const jobId = (data as { job_id?: string; id?: string }).job_id ?? (data as { id?: string }).id;
      toast.success("Book generation started!");
      router.push(`/jobs/${jobId}`);
    },
    onError: (err: Error) => {
      toast.error(err.message ?? "Failed to create job");
    },
  });

  const handleGenerate = () => {
    if (texts.length === 0) {
      toast.error("Please add at least one text");
      go(0);
      return;
    }
    const config: BookConfig = {
      name: bookName,
      texts,
      format,
    };
    createJobMutation.mutate(config);
  };

  return (
    <div className="max-w-3xl mx-auto py-10 px-4">
      {/* Step indicator */}
      <div className="mb-8">
        <ol className="flex items-center gap-0">
          {STEPS.map((s, i) => {
            const Icon = s.icon;
            const done = i < step;
            const active = i === step;
            return (
              <li key={s.id} className="flex items-center flex-1 last:flex-none">
                <button
                  type="button"
                  onClick={() => i < step && go(i)}
                  disabled={i > step}
                  className={cn(
                    "flex flex-col items-center gap-1 px-2 group focus:outline-none",
                    i > step && "cursor-not-allowed opacity-40"
                  )}
                >
                  <span
                    className={cn(
                      "flex items-center justify-center w-9 h-9 rounded-full border-2 transition-colors",
                      done && "bg-sefaria-blue border-sefaria-blue text-white",
                      active && "border-sefaria-blue text-sefaria-blue bg-white",
                      !done && !active && "border-muted-foreground/40 text-muted-foreground"
                    )}
                  >
                    {done ? (
                      <CheckCircle2 className="h-4 w-4" />
                    ) : (
                      <Icon className="h-4 w-4" />
                    )}
                  </span>
                  <span className={cn("text-[11px] font-medium hidden sm:block", active ? "text-sefaria-blue" : "text-muted-foreground")}>
                    {s.label}
                  </span>
                </button>
                {i < STEPS.length - 1 && (
                  <div className={cn("flex-1 h-0.5 mx-1", i < step ? "bg-sefaria-blue" : "bg-muted")} />
                )}
              </li>
            );
          })}
        </ol>
      </div>

      {/* Animated step content */}
      <div className="overflow-hidden">
        <AnimatePresence mode="wait" custom={dir}>
          <motion.div
            key={step}
            custom={dir}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.22, ease: "easeInOut" }}
          >
            {step === 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Choose Your Texts</CardTitle>
                  <CardDescription>
                    Search the Sefaria library and add the texts you want in your book.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-1.5">
                    <Label className="text-xs">Book Name</Label>
                    <Input
                      value={bookName}
                      onChange={(e) => setBookName(e.target.value)}
                      placeholder="My Sefaria Book"
                    />
                  </div>
                  <TextSearch onSelect={addText} />
                  {texts.length === 0 ? (
                    <div className="text-center py-10 text-muted-foreground text-sm border border-dashed rounded-lg">
                      No texts added yet. Search above to get started.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {texts.map((t, i) => (
                        <TextCard
                          key={t.link}
                          entry={t}
                          index={i}
                          onRemove={() => removeText(t.link)}
                          onChange={(u) => updateText(t.link, u)}
                        />
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {step === 1 && (
              <Card>
                <CardHeader>
                  <CardTitle>Layout &amp; Typography</CardTitle>
                  <CardDescription>
                    Configure fonts, margins, columns, and page numbering.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <BookSettingsForm value={format} onChange={setFormat} />
                </CardContent>
              </Card>
            )}

            {step === 2 && (
              <Card>
                <CardHeader>
                  <CardTitle>Cover Design</CardTitle>
                  <CardDescription>
                    Customise the cover colours and add back-cover text.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Cover preview */}
                  <div
                    className="rounded-xl border p-10 text-center space-y-2 shadow-inner"
                    style={{
                      background: format.covercolor,
                      color: format.covertextcolor,
                    }}
                  >
                    <p className="text-2xl font-bold tracking-tight">{bookName}</p>
                    {format.titleheb && (
                      <p dir="rtl" className="text-lg font-serif">
                        {format.titleheb}
                      </p>
                    )}
                    <p className="text-xs opacity-70 mt-3">
                      {texts.length} text{texts.length !== 1 ? "s" : ""}
                    </p>
                  </div>

                  {/* Reuse the cover tab from BookSettingsForm by rendering a sub-form */}
                  <BookSettingsForm value={format} onChange={setFormat} />
                </CardContent>
              </Card>
            )}

            {step === 3 && (
              <Card>
                <CardHeader>
                  <CardTitle>Review &amp; Generate</CardTitle>
                  <CardDescription>
                    Confirm your selections and generate the PDF.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Book name</p>
                    <p className="font-semibold">{bookName}</p>
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Texts ({texts.length})
                    </p>
                    {texts.length === 0 ? (
                      <p className="text-sm text-destructive">No texts — please go back and add some.</p>
                    ) : (
                      <ul className="space-y-1">
                        {texts.map((t) => (
                          <li key={t.link} className="flex items-center gap-2 text-sm">
                            <Badge variant="secondary" className="text-[10px]">
                              {t.translation || "Hebrew"}
                            </Badge>
                            <span>{t.link}</span>
                            {t.range && (
                              <span className="text-muted-foreground text-xs">({t.range})</span>
                            )}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  <Separator />

                  <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-sm">
                    <div><span className="text-muted-foreground">Paper</span> {format.paperwidth} × {format.paperheight}</div>
                    <div><span className="text-muted-foreground">Hebrew font</span> {format.hebfont}</div>
                    <div><span className="text-muted-foreground">English font</span> {format.engfont}</div>
                    <div><span className="text-muted-foreground">Layout</span> {format.layout === "twocol" ? "Two columns" : "Single column"}</div>
                    <div><span className="text-muted-foreground">Cover type</span> {format.covertype}</div>
                    <div>
                      <span className="text-muted-foreground">Cover colour </span>
                      <span
                        className="inline-block w-3 h-3 rounded-full border align-middle ml-1"
                        style={{ background: format.covercolor }}
                      />
                    </div>
                  </div>

                  <Button
                    size="lg"
                    className="w-full bg-sefaria-blue hover:bg-sefaria-blue-hover text-white"
                    onClick={handleGenerate}
                    disabled={createJobMutation.isPending || texts.length === 0}
                  >
                    {createJobMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generating…
                      </>
                    ) : (
                      "Generate PDF"
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <Button
          variant="outline"
          onClick={() => go(step - 1)}
          disabled={step === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        {step < STEPS.length - 1 && (
          <Button
            onClick={() => go(step + 1)}
            className="bg-sefaria-blue hover:bg-sefaria-blue-hover text-white"
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        )}
      </div>
    </div>
  );
}
