import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../auth/AuthProvider";

export function ProtectedRoute() {
  const { isAuthenticated, isBootstrapping } = useAuth();
  const location = useLocation();

  if (isBootstrapping) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-primary">
        <div className="glass-card rounded-2xl px-6 py-4 font-semibold">Evasym</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
