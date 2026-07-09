import { Outlet } from "react-router-dom";

import { AppBackground } from "../components/Background";

export function PublicLayout() {
  return (
    <div className="app-shell relative isolate min-h-screen overflow-hidden text-on-surface">
      <AppBackground />
      <div className="relative z-10">
        <Outlet />
      </div>
    </div>
  );
}
