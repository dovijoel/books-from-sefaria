"use client";

import { useEffect, useRef } from "react";
import { HexColorPicker } from "react-colorful";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

interface ColorPickerProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
}

export function ColorPicker({ value, onChange, label }: ColorPickerProps) {
  return (
    <div className="space-y-1.5">
      {label && <Label className="text-xs">{label}</Label>}
      <Popover>
        <PopoverTrigger
          type="button"
          className="flex items-center gap-2 h-9 w-full rounded-md border border-input bg-background px-3 text-sm hover:bg-accent transition-colors focus:outline-none focus:ring-2 focus:ring-ring"
          aria-label={label ?? "Pick a colour"}
        >
          <span
            className="inline-block w-5 h-5 rounded border border-black/20 flex-shrink-0"
            style={{ background: value }}
          />
          <span className="font-mono text-xs text-muted-foreground">{value}</span>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-3 space-y-2" align="start">
          <HexColorPicker color={value} onChange={onChange} />
          <Input
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="#000000"
            className="h-8 text-xs font-mono"
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
