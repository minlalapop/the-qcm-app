import { ArrowRight, BookOpen, Download, FileQuestion, FileText, Network, RefreshCw, Sparkles, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { listDocuments } from "../api/documents";
import { listExportJobs } from "../api/exports";
import { listReviews } from "../api/evaluation";
import { listMindmaps, listQcms, listSummaries } from "../api/generation";
import type { DocumentSummary, Evaluation, ExportJob, MindMap, QCM, Summary } from "../api/types";
import { useAuth } from "../auth/AuthProvider";
import { MetricCard } from "../components/MetricCard";
import { formatDate } from "../utils/format";

type ActivityItem = {
  id: string;
  title: string;
  type: string;
  status: string;
  date: string;
};

export function DashboardPage() {
  const { accessToken, user } = useAuth();
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [qcms, setQcms] = useState<QCM[]>([]);
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [mindmaps, setMindmaps] = useState<MindMap[]>([]);
  const [exportJobs, setExportJobs] = useState<ExportJob[]>([]);
  const [reviews, setReviews] = useState<Evaluation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void refresh();
  }, [accessToken]);

  async function refresh() {
    if (!accessToken) return;
    setIsLoading(true);
    setError(null);
    try {
      const [docs, exams, summaryItems, mapItems, jobs, reviewItems] = await Promise.all([
        listDocuments(accessToken).catch(() => []),
        listQcms(accessToken).catch(() => []),
        listSummaries(accessToken).catch(() => []),
        listMindmaps(accessToken).catch(() => []),
        listExportJobs(accessToken).catch(() => []),
        listReviews(accessToken).catch(() => []),
      ]);
      setDocuments(docs);
      setQcms(exams);
      setSummaries(summaryItems);
      setMindmaps(mapItems);
      setExportJobs(jobs);
      setReviews(reviewItems);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load dashboard");
    } finally {
      setIsLoading(false);
    }
  }

  const activities = useMemo<ActivityItem[]>(() => {
    return [
      ...qcms.map((qcm) => ({ id: qcm.id, title: qcm.title, type: "QCM", status: qcm.status, date: qcm.created_at })),
      ...summaries.map((summary) => ({ id: summary.id, title: summary.title, type: "Summary", status: "ready", date: summary.created_at })),
      ...mindmaps.map((mindmap) => ({ id: mindmap.id, title: mindmap.title, type: "Mindmap", status: mindmap.output_format, date: mindmap.created_at })),
      ...documents.map((document) => ({ id: document.id, title: document.original_filename, type: "PDF", status: document.status, date: document.created_at })),
      ...exportJobs.map((job) => ({ id: job.id, title: `${job.resource_type} ${job.export_format}`, type: "Export", status: job.status, date: job.created_at })),
    ]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, 8);
  }, [documents, exportJobs, mindmaps, qcms, summaries]);

  const averageRating =
    reviews.length > 0 ? (reviews.reduce((total, review) => total + review.rating, 0) / reviews.length).toFixed(1) : "-";

  return (
    <div className="space-y-10">
      <section className="flex flex-col gap-3 rounded-[2rem] glass-card p-5 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-[0.14em] text-primary">
            <Sparkles size={16} />
            Live workspace
          </p>
          <h2 className="mt-2 font-display text-3xl font-extrabold tracking-normal text-on-surface">Backend-connected dashboard</h2>
          <p className="mt-1 text-on-surface-variant">Counts and traceability come from your actual microservices.</p>
        </div>
        <button
          onClick={refresh}
          className="flex w-fit items-center gap-2 rounded-full bg-white/70 px-4 py-2 text-sm font-bold text-primary transition hover:bg-white"
        >
          <RefreshCw size={17} className={isLoading ? "animate-spin" : ""} />
          Refresh
        </button>
      </section>

      {error && <p className="rounded-2xl bg-error-container px-4 py-3 text-sm font-bold text-error">{error}</p>}

      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <MetricCard icon={FileQuestion} label="QCM Generated" value={String(qcms.length)} detail={`${qcms.reduce((sum, qcm) => sum + qcm.questions.length, 0)} questions total`} />
        <MetricCard icon={Users} label="Active Teachers" value={user ? "1" : "0"} detail={user?.email ?? "No teacher session"} tone="secondary" />
        <MetricCard icon={Network} label="Mindmaps Created" value={String(mindmaps.length)} detail={`${summaries.length} summaries generated`} tone="tertiary" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <div>
          <div className="mb-6 flex items-center justify-between gap-4">
            <h2 className="font-display text-2xl font-bold tracking-normal text-on-surface">Traceability</h2>
            <Link to="/dashboard/material-maker" className="text-sm font-extrabold text-primary transition hover:underline">
              Create material
            </Link>
          </div>
          <div className="glass-card overflow-hidden rounded-[2rem]">
            <div className="hidden grid-cols-[1.4fr_0.8fr_0.8fr_0.8fr] border-b border-white/50 px-8 py-4 text-left text-[11px] font-extrabold uppercase tracking-[0.14em] text-on-surface-variant md:grid">
              <span>Item</span>
              <span>Type</span>
              <span>Status</span>
              <span>Date</span>
            </div>
            <div className="divide-y divide-white/40">
              {activities.map((activity) => (
                <article key={`${activity.type}-${activity.id}`} className="grid gap-3 px-5 py-5 md:grid-cols-[1.4fr_0.8fr_0.8fr_0.8fr] md:items-center md:px-8">
                  <p className="truncate font-bold text-on-surface">{activity.title}</p>
                  <p className="text-sm font-semibold text-on-surface-variant">{activity.type}</p>
                  <span className="w-fit rounded-full bg-primary/10 px-3 py-1 text-xs font-extrabold text-primary">{activity.status}</span>
                  <p className="text-sm text-on-surface-variant">{formatDate(activity.date)}</p>
                </article>
              ))}
              {activities.length === 0 && <p className="px-8 py-8 text-sm text-on-surface-variant">No backend activity yet.</p>}
            </div>
          </div>
        </div>

        <aside className="space-y-6">
          <section className="glass-card rounded-[2rem] p-6">
            <h3 className="font-display text-2xl font-bold">Pipeline status</h3>
            <div className="mt-5 space-y-4">
              <StatusRow icon={FileText} label="PDF documents" value={documents.length} />
              <StatusRow icon={BookOpen} label="Summaries" value={summaries.length} />
              <StatusRow icon={Download} label="Export jobs" value={exportJobs.length} />
              <StatusRow icon={Sparkles} label="Average review" value={averageRating} />
            </div>
          </section>

          <section className="glass-card rounded-[2rem] p-6">
            <h3 className="font-display text-2xl font-bold">Quick creation</h3>
            <div className="mt-5 space-y-3">
              <QuickLink to="/dashboard/material-maker" icon={FileQuestion} label="Generate QCM" />
              <QuickLink to="/dashboard/material-maker" icon={BookOpen} label="Create summary" />
              <QuickLink to="/dashboard/material-maker" icon={Network} label="Build mindmap" />
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}

function StatusRow({ icon: Icon, label, value }: { icon: typeof FileText; label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between rounded-2xl bg-white/60 px-4 py-3">
      <span className="flex items-center gap-3 text-sm font-bold text-on-surface-variant">
        <Icon size={18} />
        {label}
      </span>
      <span className="font-display text-xl font-extrabold text-primary">{value}</span>
    </div>
  );
}

function QuickLink({ to, icon: Icon, label }: { to: string; icon: typeof FileText; label: string }) {
  return (
    <Link className="flex items-center justify-between rounded-2xl bg-white/60 px-4 py-3 text-sm font-bold text-on-surface transition hover:bg-primary/10 hover:text-primary" to={to}>
      <span className="flex items-center gap-3">
        <Icon size={18} />
        {label}
      </span>
      <ArrowRight size={17} />
    </Link>
  );
}
