import { createBrowserRouter, Navigate } from "react-router-dom";

import { ProtectedRoute } from "./components/ProtectedRoute";
import { DashboardLayout } from "./layouts/DashboardLayout";
import { PublicLayout } from "./layouts/PublicLayout";
import { AuthPage } from "./pages/AuthPage";
import { ComingSoonPage } from "./pages/ComingSoonPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LandingPage } from "./pages/LandingPage";
import { MaterialMakerPage } from "./pages/MaterialMakerPage";
import { MindmapsPage } from "./pages/MindmapsPage";
import { MyExamsPage } from "./pages/MyExamsPage";

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { path: "/", element: <LandingPage /> },
      { path: "/login", element: <AuthPage mode="login" /> },
      { path: "/register", element: <AuthPage mode="register" /> },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: "/dashboard",
        element: <DashboardLayout />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: "material-maker", element: <MaterialMakerPage /> },
          { path: "exams", element: <MyExamsPage /> },
          { path: "mindmaps", element: <MindmapsPage /> },
          { path: "settings", element: <ComingSoonPage title="Settings" /> },
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
