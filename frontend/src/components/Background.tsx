export function AppBackground() {
  return (
    <>
      <div className="pointer-events-none fixed inset-0 z-0 soft-gradient-bg" />
      <div className="pointer-events-none fixed inset-0 z-0 dot-mesh-bg" />
      <div className="pointer-events-none fixed inset-0 z-0 grid-bg" />

      <div className="floating-3d shape-card left-[4%] top-[14%] z-0" />
      <div className="floating-3d shape-cube right-[7%] top-[17%] z-0 delay-soft-1" />
      <div className="floating-3d shape-ring bottom-[11%] left-[10%] z-0 delay-soft-2" />
      <div className="floating-3d shape-pillar bottom-[17%] right-[14%] z-0 delay-soft-3" />
      <div className="floating-3d shape-diamond left-[48%] top-[10%] z-0 delay-soft-2" />
    </>
  );
}
