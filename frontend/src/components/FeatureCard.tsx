import type { LucideIcon } from "lucide-react";

export function FeatureCard({
  icon: Icon,
  title,
  description,
  tone = "primary",
  large = false,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  tone?: "primary" | "secondary" | "tertiary";
  large?: boolean;
}) {
  const toneClass = {
    primary: "text-primary bg-primary/10",
    secondary: "text-secondary bg-secondary/10",
    tertiary: "text-tertiary bg-tertiary-container/70",
  }[tone];

  return (
    <article
      className={`glass-card rounded-[1.75rem] p-8 transition duration-300 hover:-translate-y-1 hover:shadow-soft ${
        large ? "md:col-span-8" : "md:col-span-4"
      }`}
    >
      <div className="flex h-full flex-col gap-6">
        <div className={`flex h-16 w-16 items-center justify-center rounded-2xl ${toneClass}`}>
          <Icon size={34} strokeWidth={2.1} />
        </div>
        <div>
          <h3 className="font-display text-2xl font-bold tracking-normal text-on-surface">{title}</h3>
          <p className="mt-3 max-w-2xl text-base leading-7 text-on-surface-variant">{description}</p>
        </div>
      </div>
    </article>
  );
}
