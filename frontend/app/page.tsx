import Link from "next/link";
import { BookOpen, BookMarked, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const FEATURES = [
  {
    icon: "📜",
    title: "Search All of Sefaria",
    description:
      "Access the entire Sefaria library — Torah, Talmud, Midrash, Halakha, and more — to build your book.",
  },
  {
    icon: "🖋️",
    title: "Include Commentaries",
    description:
      "Add Rashi, Tosafot, Ramban, and dozens of other classical commentators alongside each text.",
  },
  {
    icon: "🎨",
    title: "Custom Typesetting",
    description:
      "Choose paper size, fonts, margins, spacing, and cover colours to produce a truly professional PDF.",
  },
  {
    icon: "⚡",
    title: "Fast PDF Generation",
    description:
      "Powered by LaTeX on the backend, your book is compiled to a high-quality PDF in seconds.",
  },
  {
    icon: "💾",
    title: "Save Your Configurations",
    description:
      "Save and reuse your favourite book layouts. Iterate quickly without starting from scratch.",
  },
  {
    icon: "🌍",
    title: "Hebrew & English",
    description:
      "Full RTL Hebrew support alongside English translations. Every text rendered beautifully.",
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* ── Hero ── */}
      <section className="bg-sefaria-dark text-white pt-24 pb-28 px-4 text-center relative overflow-hidden">
        {/* decorative gold line */}
        <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-sefaria-gold to-transparent" />

        <div className="max-w-3xl mx-auto">
          <Badge className="mb-6 bg-sefaria-gold/20 text-sefaria-gold border-sefaria-gold/30 hover:bg-sefaria-gold/30">
            Powered by Sefaria
          </Badge>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight mb-6">
            Turn Jewish Texts into{" "}
            <span className="text-sefaria-gold">Beautiful Books</span>
          </h1>

          <p className="text-lg sm:text-xl text-white/75 mb-10 max-w-2xl mx-auto">
            Select texts from the entire Sefaria library, add commentaries, customise
            typography and layout, then generate a professionally typeset PDF — all in minutes.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/builder">
              <Button
                size="lg"
                className="bg-sefaria-gold hover:bg-sefaria-gold-light text-sefaria-dark font-semibold px-8 text-base"
              >
                Start Building
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/configs">
              <Button
                size="lg"
                variant="outline"
                className="bg-transparent border-white/30 text-white hover:bg-white/10 px-8 text-base"
              >
                <BookMarked className="mr-2 h-5 w-5" />
                Saved Configs
              </Button>
            </Link>
          </div>
        </div>

        {/* Hebrew tagline */}
        <p dir="rtl" className="mt-10 text-white/40 text-lg font-serif">
          ספרייה של ידע יהודי
        </p>
      </section>

      {/* ── Features ── */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold text-sefaria-dark mb-4">
              Everything you need to create your book
            </h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto">
              A powerful yet simple workflow from text selection to print-ready PDF.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((feature) => (
              <Card
                key={feature.title}
                className="border hover:shadow-md transition-shadow hover:border-sefaria-gold/40"
              >
                <CardHeader className="pb-2">
                  <div className="text-3xl mb-2">{feature.icon}</div>
                  <CardTitle className="text-sefaria-dark text-lg">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="py-20 px-4 bg-sefaria-light-blue">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-sefaria-dark mb-4">
            How it works
          </h2>
          <p className="text-muted-foreground mb-12">Four simple steps to your book.</p>

          <ol className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 text-left">
            {[
              { n: "1", title: "Choose texts", body: "Search and add any text from Sefaria — with optional commentaries." },
              { n: "2", title: "Set layout", body: "Pick fonts, paper size, margins, and spacing to match your vision." },
              { n: "3", title: "Design cover", body: "Add a title, pick colours, and personalise your book cover." },
              { n: "4", title: "Download PDF", body: "Generate and download a print-ready PDF in seconds." },
            ].map((step) => (
              <li key={step.n} className="relative pl-0">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 rounded-full bg-sefaria-blue text-white text-sm font-bold flex items-center justify-center flex-shrink-0">
                    {step.n}
                  </div>
                  <h3 className="font-semibold text-sefaria-dark">{step.title}</h3>
                </div>
                <p className="text-muted-foreground text-sm pl-11">{step.body}</p>
              </li>
            ))}
          </ol>

          <Link href="/builder" className="inline-block mt-14">
            <Button
              size="lg"
              className="bg-sefaria-blue hover:bg-sefaria-blue-hover text-white font-semibold px-10 text-base"
            >
              <BookOpen className="mr-2 h-5 w-5" />
              Create Your Book
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
