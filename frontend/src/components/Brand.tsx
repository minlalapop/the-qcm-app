import { Link } from "react-router-dom";

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link to="/" className="flex items-center gap-3" aria-label="Iktibar home">
      <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/70 p-1.5 shadow-soft ring-1 ring-white/70">
        <img
          src="https://img.icons8.com/glassmorphism/96/graduation-cap.png"
          alt=""
          className="h-full w-full object-contain"
          aria-hidden="true"
        />
      </span>
      {!compact && (
        <span>
          <span className="block font-display text-2xl font-extrabold tracking-normal text-primary">Iktibar</span>
          <span className="block text-xs font-semibold uppercase tracking-[0.14em] text-on-surface-variant/70">
            Education made easier
          </span>
        </span>
      )}
    </Link>
  );
}
