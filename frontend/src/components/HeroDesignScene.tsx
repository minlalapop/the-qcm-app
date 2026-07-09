import { BookOpen, CheckCircle2, FileQuestion, Network, SlidersHorizontal } from "lucide-react";

export function HeroDesignScene() {
  return (
    <div className="scene-3d group relative mx-auto aspect-square w-full max-w-[560px]">
      <div className="scene-grid-plane" />

      <div className="scene-panel scene-panel-main">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-extrabold uppercase tracking-[0.16em] text-primary">QCM Builder</p>
            <h2 className="mt-1 font-display text-3xl font-extrabold tracking-normal text-on-surface">Custom exam</h2>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-white shadow-soft">
            <FileQuestion size={24} />
          </div>
        </div>
        <div className="space-y-3">
          <div className="h-3 w-full rounded-full bg-primary/15" />
          <div className="h-3 w-5/6 rounded-full bg-secondary/15" />
          <div className="h-3 w-2/3 rounded-full bg-tertiary/20" />
        </div>
        <div className="mt-6 grid grid-cols-3 gap-3">
          {["PDF", "Pages", "Cite"].map((label) => (
            <div key={label} className="rounded-2xl bg-white/70 px-3 py-3 text-center text-xs font-extrabold text-on-surface-variant">
              {label}
            </div>
          ))}
        </div>
      </div>

      <div className="scene-panel scene-panel-left">
        <Network className="text-secondary" size={28} />
        <span className="text-sm font-extrabold text-on-surface">Mindmap</span>
      </div>

      <div className="scene-panel scene-panel-right">
        <SlidersHorizontal className="text-primary" size={26} />
        <span className="text-sm font-extrabold text-on-surface">Difficulty</span>
      </div>

      <div className="scene-panel scene-panel-bottom">
        <BookOpen className="text-tertiary" size={26} />
        <span className="text-sm font-extrabold text-on-surface">Summary</span>
      </div>

      <div className="scene-cube scene-cube-a">
        <span />
        <span />
        <span />
      </div>
      <div className="scene-cube scene-cube-b">
        <span />
        <span />
        <span />
      </div>

      <div className="scene-badge">
        <CheckCircle2 size={18} />
        <span>Teacher approved</span>
      </div>
    </div>
  );
}
