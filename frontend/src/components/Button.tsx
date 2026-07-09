import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Link } from "react-router-dom";

type Variant = "primary" | "secondary" | "dark" | "ghost";

const variantClass: Record<Variant, string> = {
  primary: "btn-gradient text-on-primary hover:scale-[1.02] active:scale-[0.98]",
  secondary: "glass-card text-primary hover:bg-white/80 active:scale-[0.98]",
  dark: "bg-on-surface text-white hover:bg-on-surface/90 active:scale-[0.98]",
  ghost: "text-on-surface-variant hover:bg-white/70 hover:text-primary",
};

export function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-full px-5 py-2.5 text-sm font-bold transition ${variantClass[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function ButtonLink({
  children,
  to,
  variant = "primary",
  className = "",
}: {
  children: ReactNode;
  to: string;
  variant?: Variant;
  className?: string;
}) {
  return (
    <Link
      to={to}
      className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-full px-5 py-2.5 text-sm font-bold transition ${variantClass[variant]} ${className}`}
    >
      {children}
    </Link>
  );
}
