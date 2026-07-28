import { Link } from "react-router-dom";

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link to="/" className="flex min-w-0 items-center gap-3" aria-label="Evasym home">
      <span className="flex h-12 w-16 shrink-0 items-center justify-center rounded-2xl bg-white/75 p-2 shadow-soft ring-1 ring-white/70">
        <img
          src="/uiass-logo.png"
          alt=""
          className="h-full w-full object-contain"
          aria-hidden="true"
        />
      </span>
      {!compact && (
        <span className="min-w-0">
          <span className="block font-display text-2xl font-extrabold tracking-normal text-primary">Evasym</span>
          <span className="block text-xs font-semibold uppercase tracking-[0.14em] text-on-surface-variant/70">
            UIASS study material maker
          </span>
        </span>
      )}
    </Link>
  );
}
