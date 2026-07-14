import {
  Bell,
  CircleHelp,
  FileText,
  LayoutDashboard,
  LogOut,
  Network,
  Settings,
  Sparkles,
  WandSparkles,
} from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthProvider";
import { AppBackground } from "../components/Background";
import { Brand } from "../components/Brand";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/dashboard/material-maker", label: "Material Maker", icon: WandSparkles },
  { to: "/dashboard/exams", label: "My Exams", icon: FileText },
  { to: "/dashboard/mindmaps", label: "Mindmaps", icon: Network },
  { to: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const displayName = user?.full_name?.split(" ")[0] || user?.email.split("@")[0] || "Teacher";
  const initial = displayName.charAt(0).toUpperCase();

  async function handleLogout() {
    await logout();
    navigate("/", { replace: true });
  }

  return (
    <div className="app-shell relative isolate min-h-screen text-on-surface">
      <AppBackground />
      <aside className="glass-nav fixed left-0 top-0 z-40 hidden h-screen w-72 flex-col border-r px-4 py-8 lg:flex">
        <div className="px-3">
          <Brand />
        </div>

        <nav className="mt-10 flex-1 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/dashboard"}
                className={({ isActive }) =>
                  `flex items-center gap-4 rounded-xl px-4 py-3 text-sm font-bold transition ${
                    isActive
                      ? "bg-primary/10 text-primary shadow-[inset_4px_0_0_#1DA37D]"
                      : "text-on-surface-variant hover:bg-white/60 hover:text-primary"
                  }`
                }
              >
                <Icon size={20} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        <div className="space-y-3 border-t border-white/50 pt-5">
          <button className="flex w-full items-center gap-4 rounded-xl px-4 py-3 text-sm font-bold text-on-surface-variant transition hover:bg-white/60 hover:text-primary">
            <CircleHelp size={20} />
            Help Center
          </button>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-4 rounded-xl px-4 py-3 text-sm font-bold text-on-surface-variant transition hover:bg-error-container hover:text-error"
          >
            <LogOut size={20} />
            Log out
          </button>
          <p className="px-4 text-[11px] font-semibold uppercase tracking-[0.16em] text-on-surface-variant/60">
            © 2026 Iktibar
          </p>
        </div>
      </aside>

      <main className="relative z-10 min-h-screen px-4 py-6 sm:px-6 lg:ml-72 lg:px-10 lg:py-10">
        <header className="mb-9 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mb-2 flex items-center gap-2 text-sm font-bold uppercase tracking-[0.14em] text-primary">
              <Sparkles size={16} />
              Iktibar workspace
            </p>
            <h1 className="font-display text-4xl font-extrabold tracking-normal text-on-surface sm:text-5xl">
              Welcome back, {displayName}
            </h1>
            <p className="mt-2 text-lg text-on-surface-variant">Ready to craft some inspiring material today?</p>
          </div>

          <div className="flex items-center gap-3">
            <button className="glass-card flex h-12 w-12 items-center justify-center rounded-full text-on-surface-variant transition hover:text-primary">
              <Bell size={20} />
            </button>
            <div className="glass-card flex items-center gap-3 rounded-full px-3 py-2">
              <div className="flex h-9 w-9 rotate-45 items-center justify-center rounded-xl bg-primary text-white">
                <span className="-rotate-45 text-sm font-extrabold">{initial}</span>
              </div>
              <span className="pr-2 text-sm font-bold">{displayName}</span>
            </div>
          </div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
