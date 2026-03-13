"use client";

import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { ColorPicker } from "@/components/color-picker";
import { MarginControl } from "@/components/margin-control";
import {
  BookFormatSettings,
  HEBREW_FONTS,
  ENGLISH_FONTS,
  DEFAULT_FORMAT,
} from "@/lib/types";

const formatSchema = z.object({
  paperheight: z.string().min(1),
  paperwidth: z.string().min(1),
  hebfont: z.string().min(1),
  hebboldfont: z.string().min(1),
  engfont: z.string().min(1),
  commentfont: z.string().min(1),
  top: z.string().min(1),
  bottom: z.string().min(1),
  inner: z.string().min(1),
  outer: z.string().min(1),
  fontsize: z.number().min(8).max(24),
  spacing: z.string().min(1),
  engfontsize: z.string().min(1),
  parskip: z.string().min(1),
  layout: z.enum(["", "twocol"]),
  twocolfootnotes: z.boolean(),
  newpage: z.union([z.literal(0), z.literal(1)]),
  pagenumloc: z.string().min(1),
  pagenumheb: z.boolean(),
  headpos: z.string().min(1),
  evenhead: z.string(),
  oddhead: z.string(),
  chapfontsize: z.string().min(1),
  covercolor: z.string().min(1),
  covertextcolor: z.string().min(1),
  covertype: z.enum(["hardcover", "softcover"]),
  backtext: z.string(),
  titleheb: z.string(),
});

export type FormatFormValues = z.infer<typeof formatSchema>;

interface BookSettingsFormProps {
  value: BookFormatSettings;
  onChange: (updated: BookFormatSettings) => void;
}

export function BookSettingsForm({ value, onChange }: BookSettingsFormProps) {
  const { control, watch, setValue, register } = useForm<FormatFormValues>({
    resolver: zodResolver(formatSchema),
    defaultValues: { ...DEFAULT_FORMAT, ...value },
    mode: "onChange",
  });

  // Propagate changes upward on every field change
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleChange = (field: keyof FormatFormValues, val: any) => {
    setValue(field, val as never);
    onChange({ ...value, [field]: val });
  };

  return (
    <Tabs defaultValue="typography" className="w-full">
      <TabsList className="w-full grid grid-cols-4 mb-6">
        <TabsTrigger value="typography">Typography</TabsTrigger>
        <TabsTrigger value="layout">Layout</TabsTrigger>
        <TabsTrigger value="pagination">Pages</TabsTrigger>
        <TabsTrigger value="cover">Cover</TabsTrigger>
      </TabsList>

      {/* ── Typography ── */}
      <TabsContent value="typography" className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label className="text-xs">Hebrew Font</Label>
            <Select
              value={value.hebfont}
              onValueChange={(v) => handleChange("hebfont", v)}
            >
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {HEBREW_FONTS.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">Hebrew Bold Font</Label>
            <Select
              value={value.hebboldfont}
              onValueChange={(v) => handleChange("hebboldfont", v)}
            >
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {HEBREW_FONTS.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">English Font</Label>
            <Select
              value={value.engfont}
              onValueChange={(v) => handleChange("engfont", v)}
            >
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ENGLISH_FONTS.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">Commentary Font</Label>
            <Select
              value={value.commentfont}
              onValueChange={(v) => handleChange("commentfont", v)}
            >
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ENGLISH_FONTS.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Font size */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-xs">Base Font Size</Label>
            <span className="text-xs font-mono text-muted-foreground">
              {value.fontsize}pt
            </span>
          </div>
          <Slider
            min={8}
            max={24}
            step={1}
            value={[value.fontsize]}
            onValueChange={(vals) => handleChange("fontsize", (vals as number[])[0])}
          />
        </div>

        {/* Spacing */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="space-y-1.5">
            <Label className="text-xs">Line Spacing</Label>
            <Select
              value={value.spacing}
              onValueChange={(v) => handleChange("spacing", v)}
            >
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {["1", "1.25", "1.5", "1.75", "2"].map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}×
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">English Font Size</Label>
            <Input
              value={value.engfontsize}
              onChange={(e) => handleChange("engfontsize", e.target.value)}
              placeholder="11pt"
              className="h-9"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">Paragraph Skip</Label>
            <Input
              value={value.parskip}
              onChange={(e) => handleChange("parskip", e.target.value)}
              placeholder="6pt"
              className="h-9"
            />
          </div>
        </div>
      </TabsContent>

      {/* ── Layout ── */}
      <TabsContent value="layout" className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label className="text-xs">Paper Width</Label>
            <Input
              value={value.paperwidth}
              onChange={(e) => handleChange("paperwidth", e.target.value)}
              placeholder="8.5in"
              className="h-9"
            />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Paper Height</Label>
            <Input
              value={value.paperheight}
              onChange={(e) => handleChange("paperheight", e.target.value)}
              placeholder="11in"
              className="h-9"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <MarginControl
            label="Top Margin"
            value={value.top}
            onChange={(v) => handleChange("top", v)}
          />
          <MarginControl
            label="Bottom Margin"
            value={value.bottom}
            onChange={(v) => handleChange("bottom", v)}
          />
          <MarginControl
            label="Inner Margin"
            value={value.inner}
            onChange={(v) => handleChange("inner", v)}
          />
          <MarginControl
            label="Outer Margin"
            value={value.outer}
            onChange={(v) => handleChange("outer", v)}
          />
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs">Column Layout</Label>
          <Select
            value={value.layout}
            onValueChange={(v) => handleChange("layout", v as "" | "twocol")}
          >
            <SelectTrigger className="h-9">
              <SelectValue placeholder="Single column" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Single column</SelectItem>
              <SelectItem value="twocol">Two columns</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {value.layout === "twocol" && (
          <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
            <Label className="text-sm cursor-pointer">
              Footnotes in two columns
            </Label>
            <Switch
              checked={value.twocolfootnotes}
              onCheckedChange={(v) => handleChange("twocolfootnotes", v)}
            />
          </div>
        )}

        <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
          <Label className="text-sm cursor-pointer">
            New page between texts
          </Label>
          <Switch
            checked={value.newpage === 1}
            onCheckedChange={(v) => handleChange("newpage", v ? 1 : 0)}
          />
        </div>
      </TabsContent>

      {/* ── Pagination ── */}
      <TabsContent value="pagination" className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label className="text-xs">Page Number Position</Label>
            <Select
              value={value.pagenumloc}
              onValueChange={(v) => handleChange("pagenumloc", v)}
            >
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {["bottom", "top", "none"].map((p) => (
                  <SelectItem key={p} value={p} className="capitalize">
                    {p}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs">Header Position</Label>
            <Select
              value={value.headpos}
              onValueChange={(v) => handleChange("headpos", v)}
            >
              <SelectTrigger className="h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {["center", "left", "right", "none"].map((p) => (
                  <SelectItem key={p} value={p} className="capitalize">
                    {p}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex items-center justify-between rounded-md border px-3 py-2.5">
          <Label className="text-sm cursor-pointer">Hebrew page numbers</Label>
          <Switch
            checked={value.pagenumheb}
            onCheckedChange={(v) => handleChange("pagenumheb", v)}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label className="text-xs">Even Page Header</Label>
            <Input
              value={value.evenhead}
              onChange={(e) => handleChange("evenhead", e.target.value)}
              placeholder="e.g. \leftmark"
              className="h-9"
            />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Odd Page Header</Label>
            <Input
              value={value.oddhead}
              onChange={(e) => handleChange("oddhead", e.target.value)}
              placeholder="e.g. \rightmark"
              className="h-9"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs">Chapter Font Size</Label>
          <Input
            value={value.chapfontsize}
            onChange={(e) => handleChange("chapfontsize", e.target.value)}
            placeholder="14pt"
            className="h-9"
          />
        </div>
      </TabsContent>

      {/* ── Cover ── */}
      <TabsContent value="cover" className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <ColorPicker
            label="Cover Background Colour"
            value={value.covercolor}
            onChange={(v) => handleChange("covercolor", v)}
          />
          <ColorPicker
            label="Cover Text Colour"
            value={value.covertextcolor}
            onChange={(v) => handleChange("covertextcolor", v)}
          />
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs">Cover Type</Label>
          <Select
            value={value.covertype}
            onValueChange={(v) =>
              handleChange("covertype", v as "hardcover" | "softcover")
            }
          >
            <SelectTrigger className="h-9">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="softcover">Softcover</SelectItem>
              <SelectItem value="hardcover">Hardcover</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs">Hebrew Title (for spine / cover)</Label>
          <Input
            dir="rtl"
            value={value.titleheb}
            onChange={(e) => handleChange("titleheb", e.target.value)}
            placeholder="עברית"
            className="h-9"
          />
        </div>

        <div className="space-y-1.5">
          <Label className="text-xs">Back Cover Text</Label>
          <Textarea
            value={value.backtext}
            onChange={(e) => handleChange("backtext", e.target.value)}
            placeholder="Add a description or dedication for the back cover…"
            rows={4}
          />
        </div>

        {/* Live preview swatch */}
        <div
          className="rounded-lg p-6 text-center space-y-1 border"
          style={{
            background: value.covercolor,
            color: value.covertextcolor,
          }}
        >
          <p className="text-lg font-bold">Cover Preview</p>
          {value.titleheb && (
            <p dir="rtl" className="text-base font-serif">
              {value.titleheb}
            </p>
          )}
        </div>
      </TabsContent>
    </Tabs>
  );
}
