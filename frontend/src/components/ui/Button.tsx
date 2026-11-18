import type { ComponentPropsWithoutRef } from "react";
import { Link, type LinkProps } from "react-router-dom";
import { cn } from "../../lib/cn";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

const baseStyles =
  "inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition duration-200 motion-reduce:transition-none disabled:cursor-not-allowed disabled:opacity-50";

const variantStyles: Record<Variant, string> = {
  primary:
    "bg-brand-500 text-white shadow-lg shadow-brand-500/25 hover:bg-brand-400",
  secondary:
    "border border-white/15 bg-white/5 text-slate-100 hover:border-brand-400/60 hover:bg-white/10",
  ghost: "text-slate-300 hover:bg-white/10 hover:text-white",
};

const sizeStyles: Record<Size, string> = {
  sm: "px-3 py-2 text-sm",
  md: "px-4 py-2.5 text-sm",
  lg: "px-5 py-3 text-base",
};

interface ButtonProps extends ComponentPropsWithoutRef<"button"> {
  variant?: Variant;
  size?: Size;
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
      {...props}
    />
  );
}

interface ButtonLinkProps extends LinkProps {
  variant?: Variant;
  size?: Size;
}

export function ButtonLink({
  variant = "primary",
  size = "md",
  className,
  ...props
}: ButtonLinkProps) {
  return (
    <Link
      className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
      {...props}
    />
  );
}
