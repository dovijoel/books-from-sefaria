"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";

interface MarginControlProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  /** min in inches, default 0.25 */
  min?: number;
  /** max in inches, default 3 */
  max?: number;
  step?: number;
}

function inchValue(v: string): number {
  const n = parseFloat(v.replace("in", "").trim());
  return isNaN(n) ? 1 : n;
}

export function MarginControl({
  label,
  value,
  onChange,
  min = 0.25,
  max = 3,
  step = 0.05,
}: MarginControlProps) {
  const numeric = inchValue(value);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label className="text-xs">{label}</Label>
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="h-7 w-20 text-xs text-right font-mono"
        />
      </div>
      <Slider
        min={min}
        max={max}
        step={step}
        value={[numeric]}
        onValueChange={(vals) => onChange(`${(vals as number[])[0].toFixed(2)}in`)}
        className="w-full"
      />
      <div className="flex justify-between text-[10px] text-muted-foreground">
        <span>{min}in</span>
        <span>{max}in</span>
      </div>
    </div>
  );
}
