import type { ComponentPropsWithoutRef } from "react";
import { cn } from "../../lib/cn";

type Tone = "neutral" | "brand" | "aqua" | "success" | "warning";

const toneStyles: Record<Tone, string> = {
  neutral: "border-white/10 bg-white/5 text-slate-300",
  brand: "border-brand-400/30 bg-brand-500/15 text-brand-200",
  aqua: "border-aqua-400/30 bg-aqua-500/10 text-aqua-300",
  success: "border-emerald-400/30 bg-emerald-500/10 text-emerald-300",
  warning: "border-amber-400/30 bg-amber-500/10 text-amber-300",
};

interface BadgeProps extends ComponentPropsWithoutRef<"span"> {
  tone?: Tone;
}

export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider",
        toneStyles[tone],
        className,
      )}
      {...props}
    />
  );
}
