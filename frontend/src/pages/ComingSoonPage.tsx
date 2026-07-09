import { Construction } from "lucide-react";

export function ComingSoonPage({ title }: { title: string }) {
  return (
    <section className="glass-card rounded-[2rem] p-10">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        <Construction size={32} />
      </div>
      <h2 className="mt-6 font-display text-3xl font-extrabold tracking-normal text-on-surface">{title}</h2>
      <p className="mt-3 max-w-2xl text-lg leading-8 text-on-surface-variant">
        This workspace section is reserved for the next frontend step. The routing and protected dashboard shell are
        already ready.
      </p>
    </section>
  );
}
