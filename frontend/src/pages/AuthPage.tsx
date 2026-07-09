import { ArrowRight, LockKeyhole, Mail, UserRound } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../api/http";
import { useAuth } from "../auth/AuthProvider";
import { Brand } from "../components/Brand";
import { Button } from "../components/Button";

export function AuthPage({ mode }: { mode: "login" | "register" }) {
  const { login, register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const target = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? "/dashboard";

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    const normalizedEmail = email.trim().toLowerCase() === "admin" ? "admin@example.com" : email.trim();
    const normalizedPassword = email.trim().toLowerCase() === "admin" && password === "admin1234" ? "admin1234" : password;
    try {
      if (mode === "login") {
        await login({ email: normalizedEmail, password: normalizedPassword });
      } else {
        await register({ email: normalizedEmail, password, full_name: fullName || undefined, role: "teacher" });
      }
      navigate(target, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not complete authentication");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto grid min-h-screen max-w-container items-center gap-10 px-4 py-10 sm:px-8 lg:grid-cols-[1fr_0.9fr] lg:px-10">
      <section className="hidden space-y-8 lg:block">
        <Brand />
        <div>
          <p className="mb-4 inline-flex rounded-full bg-primary/10 px-4 py-2 text-sm font-bold text-primary">
            Secure teacher workspace
          </p>
          <h1 className="font-display text-6xl font-extrabold leading-[1.04] tracking-normal text-on-surface">
            Create, review and export smarter QCMs.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-on-surface-variant">
            Iktibar keeps generation, evaluation, learning and export workflows separated cleanly, while giving the
            teacher one calm workspace.
          </p>
        </div>
      </section>

      <section className="glass-card mx-auto w-full max-w-lg rounded-[2rem] p-6 sm:p-8">
        <div className="mb-8 lg:hidden">
          <Brand />
        </div>
        <h2 className="font-display text-3xl font-extrabold tracking-normal text-on-surface">
          {mode === "login" ? "Welcome back" : "Create your Iktibar account"}
        </h2>
        <p className="mt-2 text-on-surface-variant">
          {mode === "login" ? "Log in to continue to your dashboard." : "Start generating specialized material."}
        </p>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          {mode === "register" && (
            <label className="block">
              <span className="mb-2 block text-sm font-bold text-on-surface">Full name</span>
              <span className="relative block">
                <UserRound className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant" size={18} />
                <input
                  className="h-12 w-full rounded-2xl border border-outline-variant bg-white/70 pl-12 pr-4 text-on-surface outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  autoComplete="name"
                />
              </span>
            </label>
          )}

          <label className="block">
            <span className="mb-2 block text-sm font-bold text-on-surface">
              {mode === "login" ? "Email or dev alias" : "Email"}
            </span>
            <span className="relative block">
              <Mail className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant" size={18} />
              <input
                className="h-12 w-full rounded-2xl border border-outline-variant bg-white/70 pl-12 pr-4 text-on-surface outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
                type={mode === "login" ? "text" : "email"}
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder={mode === "login" ? "admin or name@example.com" : "name@example.com"}
                autoComplete={mode === "login" ? "username" : "email"}
              />
            </span>
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-bold text-on-surface">Password</span>
            <span className="relative block">
              <LockKeyhole className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant" size={18} />
              <input
                className="h-12 w-full rounded-2xl border border-outline-variant bg-white/70 pl-12 pr-4 text-on-surface outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                placeholder={mode === "login" ? "admin1234" : "At least 8 characters"}
              />
            </span>
          </label>

          {error && <p className="rounded-2xl bg-error-container px-4 py-3 text-sm font-semibold text-error">{error}</p>}

          <Button className="w-full py-4" disabled={isSubmitting}>
            {isSubmitting ? "Please wait..." : mode === "login" ? "Log In" : "Create Account"}
            <ArrowRight size={18} />
          </Button>
        </form>

        <p className="mt-6 text-center text-sm font-semibold text-on-surface-variant">
          {mode === "login" ? "No account yet?" : "Already have an account?"}{" "}
          <Link className="text-primary hover:underline" to={mode === "login" ? "/register" : "/login"}>
            {mode === "login" ? "Create one" : "Log in"}
          </Link>
        </p>
      </section>
    </main>
  );
}
