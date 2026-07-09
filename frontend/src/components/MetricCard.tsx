import type { LucideIcon } from "lucide-react";

export function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
  tone = "primary",
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  detail: string;
  tone?: "primary" | "secondary" | "tertiary";
}) {
  const toneClass = {
    primary: "text-primary bg-primary/10",
    secondary: "text-secondary bg-secondary/10",
    tertiary: "text-tertiary bg-tertiary-container",
  }[tone];

  return (
    <article className="glass-card group relative overflow-hidden rounded-[1.75rem] p-7 transition hover:-translate-y-1">
      <div className={`absolute right-5 top-5 flex h-16 w-16 items-center justify-center rounded-2xl opacity-15 ${toneClass}`}>
        <Icon size={38} />
      </div>
      <p className="mb-1 text-sm font-semibold uppercase tracking-[0.08em] text-on-surface-variant">{label}</p>
      <p className={`font-display text-5xl font-extrabold tracking-normal ${toneClass.split(" ")[0]}`}>{value}</p>
      <p className="mt-4 text-sm font-semibold text-on-surface-variant">{detail}</p>
    </article>
  );
}
