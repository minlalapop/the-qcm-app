import { Network, RefreshCw, X } from "lucide-react";
import { useEffect, useState } from "react";

import { listMindmaps, updateMindmap } from "../api/generation";
import type { MindMap } from "../api/types";
import { useAuth } from "../auth/AuthProvider";
import { Button } from "../components/Button";
import { MindmapPreview } from "../components/MindmapPreview";
import { classNames, formatDate } from "../utils/format";

export function MindmapsPage() {
  const { accessToken } = useAuth();
  const [mindmaps, setMindmaps] = useState<MindMap[]>([]);
  const [selectedMindmap, setSelectedMindmap] = useState<MindMap | null>(null);
  const [previewMindmap, setPreviewMindmap] = useState<MindMap | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void refresh();
  }, [accessToken]);

  async function refresh() {
    if (!accessToken) return;
    const data = await listMindmaps(accessToken);
    setMindmaps(data);
    setSelectedMindmap((current) => current ?? data[0] ?? null);
  }

  function patchMindmap(updated: MindMap) {
    setPreviewMindmap(updated);
    setSelectedMindmap(updated);
    setMindmaps((current) => current.map((mindmap) => (mindmap.id === updated.id ? updated : mindmap)));
  }

  return (
    <div className="space-y-6">
      <section className="glass-card rounded-[2rem] p-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="font-display text-3xl font-extrabold">My mindmaps</h1>
            <p className="mt-1 text-on-surface-variant">{mindmaps.length} generated map(s)</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={refresh}>
              <RefreshCw size={17} />
              Refresh
            </Button>
          </div>
        </div>
        {status && <p className="mt-4 rounded-2xl bg-primary/10 px-4 py-3 text-sm font-bold text-primary">{status}</p>}
        {error && <p className="mt-4 rounded-2xl bg-error-container px-4 py-3 text-sm font-bold text-error">{error}</p>}
      </section>

      <section className="glass-card rounded-[2rem] p-5">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {mindmaps.map((mindmap) => (
            <button
              key={mindmap.id}
              className={classNames(
                "min-w-0 rounded-2xl border p-4 text-left transition hover:-translate-y-0.5 hover:shadow-soft",
                selectedMindmap?.id === mindmap.id ? "border-primary/40 bg-primary/10" : "border-white/70 bg-white/55",
              )}
              onClick={() => {
                setSelectedMindmap(mindmap);
                setPreviewMindmap(mindmap);
              }}
            >
              <div className="flex gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-secondary/10 text-secondary">
                  <Network size={20} />
                </div>
                <div className="min-w-0">
                  <p className="truncate font-bold">{mindmap.title}</p>
                  <p className="text-xs text-on-surface-variant">{formatDate(mindmap.created_at)}</p>
                  <p className="mt-1 text-xs font-bold text-primary">
                    {mindmap.document_ids.length} source(s) | {mindmap.output_format}
                  </p>
                </div>
              </div>
            </button>
          ))}
          {mindmaps.length === 0 && (
            <p className="rounded-2xl bg-white/60 p-6 text-sm font-bold text-on-surface-variant">
              No mindmaps generated yet.
            </p>
          )}
        </div>
      </section>

      {previewMindmap && (
        <div
          className="fixed inset-y-0 left-0 right-0 z-50 flex items-center justify-center overflow-hidden bg-on-surface/20 p-4 backdrop-blur-sm lg:left-72"
          onClick={() => setPreviewMindmap(null)}
        >
          <section
            className="glass-card flex h-[88vh] w-full max-w-6xl min-w-0 flex-col overflow-hidden rounded-[2rem] p-5 shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between gap-3">
              <MindmapTitleEditor mindmap={previewMindmap} onChange={patchMindmap} />
              <button className="rounded-full bg-white/70 p-3 text-on-surface-variant hover:text-primary" onClick={() => setPreviewMindmap(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-auto">
              <MindmapPreview mindmap={previewMindmap} />
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

function MindmapTitleEditor({ mindmap, onChange }: { mindmap: MindMap; onChange: (mindmap: MindMap) => void }) {
  const { accessToken } = useAuth();
  const [titleDraft, setTitleDraft] = useState(mindmap.title);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    setTitleDraft(mindmap.title);
    setStatus(null);
  }, [mindmap.id, mindmap.title]);

  async function saveTitle() {
    if (!accessToken) return;
    setStatus("Saving...");
    const updated = await updateMindmap(accessToken, mindmap.id, { title: titleDraft });
    onChange(updated);
    setStatus("Saved");
  }

  return (
    <div className="min-w-0 flex-1">
      <div className="flex min-w-0 flex-col gap-2 sm:flex-row sm:items-center">
        <input
          className="h-12 min-w-0 flex-1 rounded-2xl border border-outline-variant bg-white/70 px-4 font-display text-xl font-extrabold outline-none focus:border-primary focus:ring-4 focus:ring-primary/10"
          value={titleDraft}
          onChange={(event) => setTitleDraft(event.target.value)}
        />
        <Button variant="secondary" onClick={saveTitle}>Save title</Button>
      </div>
      <p className="mt-1 text-sm text-on-surface-variant">
        {mindmap.document_ids.length} source(s) | {formatDate(mindmap.created_at)}
        {status ? ` | ${status}` : ""}
      </p>
    </div>
  );
}
