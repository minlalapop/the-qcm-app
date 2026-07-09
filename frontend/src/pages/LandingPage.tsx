import { ArrowRight, BookOpen, CheckCircle2, FileQuestion, GraduationCap, Network, Sparkles, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { Brand } from "../components/Brand";
import { ButtonLink } from "../components/Button";
import { FeatureCard } from "../components/FeatureCard";
import { HeroDesignScene } from "../components/HeroDesignScene";

export function LandingPage() {
  return (
    <>
      <nav className="glass-nav fixed left-0 top-0 z-50 flex w-full items-center justify-between border-b px-4 py-4 sm:px-8 lg:px-10">
        <Brand />
        <div className="hidden items-center gap-8 md:flex">
          <a className="text-sm font-bold text-primary" href="#features">
            Features
          </a>
        </div>
        <div className="flex items-center gap-3">
          <Link className="hidden text-sm font-bold text-on-surface-variant transition hover:text-primary sm:inline-flex" to="/login">
            Log In
          </Link>
          <ButtonLink to="/register" className="px-5">
            Get Started
          </ButtonLink>
        </div>
      </nav>

      <main className="pt-28">
        <section className="mx-auto grid max-w-container items-center gap-12 px-4 py-12 sm:px-8 lg:grid-cols-2 lg:px-10 lg:py-20">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-bold text-primary">
              <Sparkles size={17} />
              Smart tools for specialized QCMs
            </div>
            <div className="space-y-5">
              <h1 className="font-display text-5xl font-extrabold leading-[1.05] tracking-normal text-on-surface sm:text-6xl">
                Empower Your <span className="text-primary">Teaching</span> with Smart Precision
              </h1>
              <p className="max-w-xl text-lg leading-8 text-on-surface-variant">
                Generate high-quality QCM exams, focused summaries, and Mermaid mindmaps from your course PDFs. Keep the
                control, customize the output, and save the time.
              </p>
            </div>
            <div className="flex flex-wrap gap-4">
              <ButtonLink to="/register" className="px-7 py-4">
                Start Creating
                <ArrowRight size={18} />
              </ButtonLink>
              <ButtonLink to="/login" variant="secondary" className="px-7 py-4">
                Explore Dashboard
              </ButtonLink>
            </div>
            <div className="flex flex-wrap items-center gap-5 pt-2">
              <div className="flex -space-x-3">
                {[GraduationCap, Sparkles, BookOpen].map((Icon, index) => (
                  <div
                    key={index}
                    className="flex h-11 w-11 items-center justify-center rounded-full border-2 border-white bg-white text-primary shadow-soft"
                  >
                    <Icon size={19} />
                  </div>
                ))}
              </div>
              <p className="text-sm font-semibold text-on-surface-variant">
                Built for teachers who need precise, editable learning material.
              </p>
            </div>
          </div>

          <HeroDesignScene />
        </section>

        <section id="features" className="mx-auto max-w-container px-4 py-16 sm:px-8 lg:px-10">
          <div className="mb-12 text-center">
            <span className="rounded-full bg-primary/10 px-4 py-2 text-xs font-extrabold uppercase tracking-[0.18em] text-primary">
              Capabilities
            </span>
            <h2 className="mt-5 font-display text-4xl font-extrabold tracking-normal text-on-surface">
              Designed for the Modern Educator
            </h2>
          </div>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
            <FeatureCard
              large
              icon={FileQuestion}
              title="Precision QCM Generation"
              description="Choose documents, pages, course passages, number of questions, number of options, difficulty level, and custom generation rules."
            />
            <FeatureCard
              icon={Network}
              tone="secondary"
              title="Visual Mindmaps"
              description="Turn complex course concepts into Mermaid diagrams and export them as code or PNG."
            />
            <FeatureCard
              icon={BookOpen}
              tone="tertiary"
              title="Smart Summaries"
              description="Generate concise, organized summaries from selected sources without wasting tokens."
            />
            <FeatureCard
              large
              icon={Users}
              title="Human Feedback Loop"
              description="Teachers can review generated questions, correct them, and feed the learning service with reusable quality rules."
            />
          </div>
        </section>

        <section className="mx-auto max-w-container px-4 py-16 sm:px-8 lg:px-10">
          <div className="glass-card overflow-hidden rounded-[2rem] px-6 py-14 text-center sm:px-10">
            <h2 className="mx-auto max-w-2xl font-display text-4xl font-extrabold tracking-normal text-on-surface">
              Ready to create your first specialized QCM?
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-on-surface-variant">
              Start with a PDF, customize the generation settings, review the questions, then export your final material.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
              <ButtonLink to="/register" className="px-8 py-4">
                Create Account
                <CheckCircle2 size={18} />
              </ButtonLink>
              <ButtonLink to="/login" variant="dark" className="px-8 py-4">
                Log In
              </ButtonLink>
            </div>
          </div>
        </section>
      </main>

      <footer className="glass-nav border-t px-4 py-8 sm:px-8 lg:px-10">
        <div className="mx-auto flex max-w-container flex-col items-center justify-between gap-4 text-sm font-semibold text-on-surface-variant md:flex-row">
          <Brand compact />
          <p>© 2026 Iktibar. All rights reserved.</p>
          <div className="flex gap-6">
            <a className="transition hover:text-primary" href="#privacy">
              Privacy
            </a>
            <a className="transition hover:text-primary" href="#terms">
              Terms
            </a>
          </div>
        </div>
      </footer>
    </>
  );
}
