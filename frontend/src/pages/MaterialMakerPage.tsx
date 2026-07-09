import {
  BookOpen,
  Download,
  FileQuestion,
  FileText,
  FileUp,
  Network,
  SlidersHorizontal,
  Sparkles,
  Trash2,
  X,
  Zap,
} from "lucide-react";
import { ChangeEvent, PointerEvent, ReactNode, useEffect, useMemo, useState } from "react";

import { deleteDocument, getDocumentPageImageUrls, listDocuments, uploadDocument } from "../api/documents";
import { downloadExport, exportMindmap, exportQcm, exportSummary } from "../api/exports";
import { generateMindmap, generateQcm, generateSummary, updateMindmap, updateSummary } from "../api/generation";
import { indexDocument, listIndexes } from "../api/knowledge";
import * as authApi from "../auth/authApi";
import type { DocumentSummary, KnowledgeIndex, MindMap, QCM, SourceSelection, Summary } from "../api/types";
import { useAuth } from "../auth/AuthProvider";
import { Button } from "../components/Button";
import { MindmapPreview } from "../components/MindmapPreview";
import { QcmEditor } from "../components/QcmEditor";
import { classNames, formatBytes, formatDate } from "../utils/format";

type MakerMode = "qcm" | "summary" | "mindmap";
type ModalMode = "configure" | "preview" | "export" | null;

export function MaterialMakerPage() {
  const { accessToken, logout } = useAuth();
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [indexes, setIndexes] = useState<KnowledgeIndex[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [previewDocumentId, setPreviewDocumentId] = useState<string | null>(null);
  const [pageImages, setPageImages] = useState<Array<{ pageNumber: number; url: string }>>([]);
  const [modal, setModal] = useState<ModalMode>(null);
  const [mode, setMode] = useState<MakerMode>("qcm");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const [title, setTitle] = useState("New material");
  const [focusText, setFocusText] = useState("");
  const [pageNumbers, setPageNumbers] = useState("");
  const [numberOfQuestions, setNumberOfQuestions] = useState(5);
  const [numberOfOptions, setNumberOfOptions] = useState(4);
  const [difficulty, setDifficulty] = useState("medium");
  const [topK, setTopK] = useState(6);
  const [maxSections, setMaxSections] = useState(5);
  const [resultQcm, setResultQcm] = useState<QCM | null>(null);
  const [resultSummary, setResultSummary] = useState<Summary | null>(null);
  const [resultMindmap, setResultMindmap] = useState<MindMap | null>(null);

  const selectedDocuments = useMemo(
    () => documents.filter((document) => selectedDocumentIds.includes(document.id)),
    [documents, selectedDocumentIds],
  );
  const previewDocument = documents.find((document) => document.id === previewDocumentId) ?? selectedDocuments[0] ?? documents[0] ?? null;
  const hasGeneratedMaterial = Boolean(resultQcm || resultSummary || resultMindmap);

  useEffect(() => {
    void refreshData();
  }, [accessToken]);

  useEffect(() => {
    if (!accessToken || !previewDocument?.id || modal !== "preview") {
      setPageImages([]);
      return;
    }

    let active = true;
    let urls: string[] = [];
    setPageImages([]);

    getDocumentPageImageUrls(accessToken, previewDocument.id)
      .then((images) => {
        urls = images.map((image) => image.url);
        if (active) setPageImages(images);
        else urls.forEach(URL.revokeObjectURL);
      })
      .catch((err) => {
        if (active) setError(err instanceof Error ? err.message : "Could not preview PDF");
      });

    return () => {
      active = false;
      urls.forEach(URL.revokeObjectURL);
    };
  }, [accessToken, modal, previewDocument?.id]);

  async function refreshData() {
    if (!accessToken) return;
    const [docs, knowledgeIndexes] = await Promise.all([listDocuments(accessToken), listIndexes(accessToken).catch(() => [])]);
    setDocuments(docs);
    setIndexes(knowledgeIndexes);
    if (!previewDocumentId && docs[0]) setPreviewDocumentId(docs[0].id);
  }

  async function handleUpload(event: ChangeEvent<HTMLInputElement>) {
    if (!accessToken || !event.target.files?.[0]) return;
    setError(null);
    setIsUploading(true);
    setStatus("Uploading and preparing PDF...");
    try {
      const document = await uploadDocument(accessToken, event.target.files[0]);
      setStatus("Preparing this document for AI search...");
      await indexDocument(accessToken, document.id);
      setSelectedDocumentIds((current) => [...new Set([...current, document.id])]);
      setPreviewDocumentId(document.id);
      await refreshData();
      setStatus("Document ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  async function removeDocument(documentId: string) {
    if (!accessToken) return;
    setIsUploading(true);
    try {
      await deleteDocument(accessToken, documentId);
      setSelectedDocumentIds((current) => current.filter((id) => id !== documentId));
      if (previewDocumentId === documentId) setPreviewDocumentId(null);
      await refreshData();
    } finally {
      setIsUploading(false);
    }
  }

  function openPreview(document: DocumentSummary) {
    setPreviewDocumentId(document.id);
    setModal("preview");
  }

  function toggleDocument(document: DocumentSummary, selected: boolean) {
    setSelectedDocumentIds((current) => (selected ? [...new Set([...current, document.id])] : current.filter((id) => id !== document.id)));
    setPreviewDocumentId(document.id);
  }

  function clearGeneratedMaterial() {
    setResultQcm(null);
    setResultSummary(null);
    setResultMindmap(null);
    setStatus(null);
    setError(null);
  }

  function changeMode(nextMode: MakerMode) {
    if (nextMode !== mode) {
      clearGeneratedMaterial();
    }
    setMode(nextMode);
  }

  async function ensureIndexes() {
    if (!accessToken) return;
    for (const documentId of selectedDocumentIds) {
      const existing = indexes.find((index) => index.document_id === documentId && index.status === "indexed");
      if (!existing) {
        setStatus("Preparing selected sources for AI search...");
        await indexDocument(accessToken, documentId);
      }
    }
    setIndexes(await listIndexes(accessToken).catch(() => []));
  }

  function buildSourceSelection(): SourceSelection {
    return {
      document_ids: selectedDocumentIds,
      page_numbers: parsePositiveIntegerList(pageNumbers),
      chunk_ids: [],
      focus_text: focusText || null,
    };
  }

  async function generate() {
    if (!accessToken || selectedDocumentIds.length === 0) {
      setError("Select at least one PDF source");
      return;
    }
    setError(null);
    setIsGenerating(true);
    setResultQcm(null);
    setResultSummary(null);
    setResultMindmap(null);
    try {
      try {
        await authApi.me(accessToken);
      } catch {
        await logout();
        setError("Session expired or user not found. Please log in again.");
        return;
      }
      await ensureIndexes();
      setStatus(`Generating ${mode.toUpperCase()}...`);
      const sourceSelection = buildSourceSelection();
      if (mode === "qcm") {
        setResultQcm(
          await generateQcm(accessToken, {
            title,
            source_selection: sourceSelection,
            number_of_questions: numberOfQuestions,
            number_of_options: numberOfOptions,
            difficulty,
            top_k: topK,
            temperature: 0.2,
            max_tokens: 1800,
            duplication_check: true,
            custom_rules: { require_justification: true, single_correct_answer: true },
          }),
        );
      } else if (mode === "summary") {
        setResultSummary(
          await generateSummary(accessToken, {
            title,
            source_selection: sourceSelection,
            style: "concise_structured",
            max_sections: maxSections,
            top_k: topK,
            temperature: 0.15,
            max_tokens: 2200,
            custom_rules: { concise: true, organized: true },
          }),
        );
      } else {
        setResultMindmap(
          await generateMindmap(accessToken, {
            title,
            source_selection: sourceSelection,
            output_format: "mermaid",
            top_k: Math.max(topK, 10),
            temperature: 0.2,
            max_tokens: 3600,
            custom_rules: { concise_nodes: true, rich_hierarchy: true, notebooklm_style: true },
          }),
        );
      }
      setStatus("Generation completed");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleExport(format: "pdf" | "docx" | "json" | "png" | "mermaid") {
    if (!accessToken) return;
    setError(null);
    setIsExporting(true);
    setStatus(`Exporting ${format.toUpperCase()}...`);
    try {
      let exported;
      if (resultQcm && (format === "pdf" || format === "docx" || format === "json")) {
        exported = await exportQcm(accessToken, resultQcm.id, format);
      } else if (resultSummary && (format === "pdf" || format === "docx" || format === "json")) {
        exported = await exportSummary(accessToken, resultSummary.id, format);
      } else if (resultMindmap && (format === "png" || format === "mermaid" || format === "json")) {
        exported = await exportMindmap(accessToken, resultMindmap.id, format);
      } else {
        setError("This export format is not available for the current material");
        return;
      }
      await downloadExport(accessToken, exported.id, `${exported.title}.${exported.export_format}`);
      setStatus("Export ready");
      setModal(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <div className="min-w-0 overflow-x-hidden">
      <section className="glass-card min-h-[76vh] min-w-0 overflow-hidden rounded-[2rem]">
        <div className="flex flex-col items-center gap-4 border-b border-white/60 px-5 py-5 text-center">
          <h2 className="font-display text-2xl font-extrabold text-on-surface">{title || "New material"}</h2>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <label className="inline-flex min-h-11 cursor-pointer items-center justify-center gap-2 rounded-full bg-white/70 px-5 py-2.5 text-sm font-bold text-primary transition hover:bg-white">
              <FileUp size={18} />
              Upload
              <input type="file" accept="application/pdf" className="hidden" onChange={handleUpload} />
            </label>
            <Button variant="secondary" onClick={() => setModal("configure")}>
              <SlidersHorizontal size={18} />
              Configure
            </Button>
            {!resultMindmap && (
              <Button onClick={() => setModal("export")} disabled={!hasGeneratedMaterial}>
                <Download size={18} />
                Export
              </Button>
            )}
          </div>
        </div>

        {documents.length > 0 && (
          <div className="flex min-w-0 flex-wrap justify-center gap-3 border-b border-white/50 px-5 py-4">
            {documents.map((document) => {
              const selected = selectedDocumentIds.includes(document.id);
              return (
                <article
                  key={document.id}
                  className={classNames(
                    "flex max-w-full items-center gap-3 rounded-full border px-3 py-2 text-sm font-bold transition",
                    selected ? "border-primary/40 bg-primary/10 text-primary" : "border-white/70 bg-white/60 text-on-surface-variant",
                  )}
                >
                  <button className="flex min-w-0 items-center gap-2" onClick={() => openPreview(document)}>
                    <FileText size={16} />
                    <span className="max-w-[260px] truncate">{document.original_filename}</span>
                    <span className="text-xs opacity-70">{document.page_count}p</span>
                  </button>
                  <button className="text-on-surface-variant hover:text-error" onClick={() => removeDocument(document.id)}>
                    <Trash2 size={16} />
                  </button>
                </article>
              );
            })}
          </div>
        )}

        <div className="flex min-h-[58vh] flex-col items-center justify-center px-6 py-16 text-center">
          {!hasGeneratedMaterial && (
            <>
              {isGenerating ? (
                <GeneratingPlayground />
              ) : (
                <div className="scene-3d relative mb-9 h-36 w-36">
                  <div className="scene-cube scene-cube-b left-12 top-8">
                    <span />
                    <span />
                    <span />
                  </div>
                  <div className="absolute left-11 top-12 flex h-16 w-16 rotate-6 items-center justify-center rounded-3xl bg-secondary-fixed text-primary shadow-soft">
                    <Sparkles size={30} />
                  </div>
                  <div className="absolute bottom-6 right-5 flex h-11 w-11 items-center justify-center rounded-2xl bg-white text-primary shadow-soft">
                    <FileQuestion size={22} />
                  </div>
                </div>
              )}
              <h1 className="font-display text-4xl font-extrabold tracking-normal text-on-surface sm:text-5xl">
                Create something great.
              </h1>
              <p className="mt-5 max-w-xl text-lg leading-8 text-on-surface-variant">
                Upload a source, configure the material once, then generate tailored study content.
              </p>
              <Button className="mt-9" onClick={generate} disabled={isGenerating || isUploading}>
                <Zap size={18} />
                {isGenerating ? "Generating..." : "Generate Now"}
              </Button>
            </>
          )}

          {resultQcm && (
            <div className="w-full max-w-5xl text-left">
              <QcmEditor
                qcm={resultQcm}
                documents={documents}
                onOpenSource={(documentId) => {
                  setPreviewDocumentId(documentId);
                  setModal("preview");
                }}
                onChange={setResultQcm}
                onExport={(format) => void handleExport(format)}
              />
            </div>
          )}

          {resultSummary && (
            <SummaryResult
              summary={resultSummary}
              onChange={setResultSummary}
              onExport={(format) => void handleExport(format)}
            />
          )}

          {resultMindmap && (
            <MindmapResult mindmap={resultMindmap} onChange={setResultMindmap} />
          )}

          <div className="mt-6 flex min-h-10 flex-wrap justify-center gap-3">
            {status && <span className="rounded-full bg-primary/10 px-4 py-2 text-sm font-bold text-primary">{status}</span>}
            {error && <span className="max-w-full break-words rounded-2xl bg-error-container px-4 py-2 text-sm font-bold text-error">{error}</span>}
          </div>
        </div>
      </section>

      {modal === "configure" && (
        <Modal title="Configure material" onClose={() => setModal(null)}>
          <ConfigureForm
            mode={mode}
            setMode={changeMode}
            title={title}
            setTitle={setTitle}
            pageNumbers={pageNumbers}
            setPageNumbers={setPageNumbers}
            topK={topK}
            setTopK={setTopK}
            numberOfQuestions={numberOfQuestions}
            setNumberOfQuestions={setNumberOfQuestions}
            numberOfOptions={numberOfOptions}
            setNumberOfOptions={setNumberOfOptions}
            difficulty={difficulty}
            setDifficulty={setDifficulty}
            maxSections={maxSections}
            setMaxSections={setMaxSections}
            focusText={focusText}
            setFocusText={setFocusText}
            documents={documents}
            selectedDocumentIds={selectedDocumentIds}
            onToggle={toggleDocument}
            onConfirm={() => setModal(null)}
          />
        </Modal>
      )}

      {modal === "preview" && (
        <Modal title={previewDocument?.original_filename ?? "PDF preview"} onClose={() => setModal(null)} wide>
          <div className="max-h-[72vh] overflow-auto rounded-2xl bg-surface-container-low p-4">
            {pageImages.length > 0 ? (
              <div className="space-y-5">
                {pageImages.map((page) => (
                  <figure key={page.pageNumber} className="rounded-2xl bg-white p-3 shadow-soft">
                    <figcaption className="mb-2 text-xs font-extrabold uppercase tracking-[0.14em] text-primary">
                      Page {page.pageNumber}
                    </figcaption>
                    <img src={page.url} alt={`Page ${page.pageNumber}`} className="mx-auto w-full max-w-[860px] rounded-xl bg-white" />
                  </figure>
                ))}
              </div>
            ) : (
              <div className="flex min-h-[360px] items-center justify-center text-sm font-bold text-on-surface-variant">
                Loading PDF preview...
              </div>
            )}
          </div>
        </Modal>
      )}

      {modal === "export" && (
        <Modal title="Export as" onClose={() => setModal(null)}>
          <ExportOptions
            hasGeneratedMaterial={hasGeneratedMaterial}
            resultQcm={resultQcm}
            resultSummary={resultSummary}
            resultMindmap={resultMindmap}
            onExport={(format) => void handleExport(format)}
            isBusy={isExporting}
          />
        </Modal>
      )}
    </div>
  );
}

function SummaryResult({
  summary,
  onChange,
  onExport,
}: {
  summary: Summary;
  onChange: (summary: Summary) => void;
  onExport: (format: "pdf" | "docx" | "json") => void;
}) {
  const { accessToken } = useAuth();
  const [titleDraft, setTitleDraft] = useState(summary.title);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    setTitleDraft(summary.title);
  }, [summary.id, summary.title]);

  async function saveTitle() {
    if (!accessToken) return;
    setStatus("Saving title...");
    const updated = await updateSummary(accessToken, summary.id, { title: titleDraft });
    onChange(updated);
    setStatus("Title saved for export");
  }

  return (
    <section className="glass-card w-full max-w-4xl rounded-[2rem] p-6 text-left">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <label className="min-w-0 flex-1">
          <span className="mb-2 block text-xs font-extrabold uppercase tracking-[0.14em] text-on-surface-variant">
            Summary title
          </span>
          <input
            className="h-12 w-full min-w-0 rounded-2xl border border-outline-variant bg-white/70 px-4 font-display text-xl font-bold outline-none focus:border-primary focus:ring-4 focus:ring-primary/10"
            value={titleDraft}
            onChange={(event) => setTitleDraft(event.target.value)}
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={saveTitle}>Save title</Button>
          <Button variant="ghost" onClick={() => onExport("pdf")}>
            <Download size={17} />
            PDF
          </Button>
          <Button variant="ghost" onClick={() => onExport("docx")}>DOCX</Button>
        </div>
      </div>
      <p className="mt-3 text-sm text-on-surface-variant">{formatDate(summary.created_at)}</p>
      {status && <p className="mt-4 rounded-2xl bg-primary/10 px-4 py-3 text-sm font-bold text-primary">{status}</p>}
      <div className="mt-5 min-w-0 whitespace-pre-wrap break-words rounded-2xl bg-white/65 p-5 leading-7">{summary.content}</div>
    </section>
  );
}

function MindmapResult({ mindmap, onChange }: { mindmap: MindMap; onChange: (mindmap: MindMap) => void }) {
  const { accessToken } = useAuth();
  const [titleDraft, setTitleDraft] = useState(mindmap.title);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    setTitleDraft(mindmap.title);
  }, [mindmap.id, mindmap.title]);

  async function saveTitle() {
    if (!accessToken) return;
    setStatus("Saving title...");
    const updated = await updateMindmap(accessToken, mindmap.id, { title: titleDraft });
    onChange(updated);
    setStatus("Title saved");
  }

  return (
    <section className="glass-card w-full max-w-4xl rounded-[2rem] p-6 text-left">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <label className="min-w-0 flex-1">
          <span className="mb-2 block text-xs font-extrabold uppercase tracking-[0.14em] text-on-surface-variant">
            Mindmap title
          </span>
          <input
            className="h-12 w-full min-w-0 rounded-2xl border border-outline-variant bg-white/70 px-4 font-display text-xl font-bold outline-none focus:border-primary focus:ring-4 focus:ring-primary/10"
            value={titleDraft}
            onChange={(event) => setTitleDraft(event.target.value)}
          />
        </label>
        <Button variant="secondary" onClick={saveTitle}>Save title</Button>
      </div>
      {status && <p className="mt-4 rounded-2xl bg-primary/10 px-4 py-3 text-sm font-bold text-primary">{status}</p>}
      <MindmapPreview mindmap={mindmap} />
    </section>
  );
}

function GeneratingPlayground() {
  const shapes = useMemo(
    () => [
      { id: 1, x: 16, y: 28, size: 18, kind: "circle", color: "rgba(134,45,190,0.24)" },
      { id: 2, x: 30, y: 68, size: 22, kind: "triangle", color: "rgba(36,163,255,0.24)" },
      { id: 3, x: 44, y: 22, size: 16, kind: "square", color: "rgba(156,93,229,0.22)" },
      { id: 4, x: 58, y: 60, size: 20, kind: "circle", color: "rgba(134,45,190,0.18)" },
      { id: 5, x: 72, y: 34, size: 24, kind: "triangle", color: "rgba(36,163,255,0.2)" },
      { id: 6, x: 84, y: 72, size: 17, kind: "square", color: "rgba(134,45,190,0.24)" },
      { id: 7, x: 22, y: 78, size: 14, kind: "circle", color: "rgba(156,93,229,0.24)" },
      { id: 8, x: 78, y: 18, size: 15, kind: "circle", color: "rgba(134,45,190,0.18)" },
      { id: 9, x: 50, y: 78, size: 19, kind: "triangle", color: "rgba(134,45,190,0.18)" },
      { id: 10, x: 62, y: 25, size: 14, kind: "square", color: "rgba(36,163,255,0.18)" },
    ],
    [],
  );
  const [eaten, setEaten] = useState<number[]>([]);
  const [score, setScore] = useState(0);
  const [player, setPlayer] = useState({ x: 50, y: 52 });
  const playerSize = 48 + Math.min(score, 34) * 1.2;

  function moveShapes(event: PointerEvent<HTMLDivElement>) {
    const bounds = event.currentTarget.getBoundingClientRect();
    const nextPlayer = {
      x: ((event.clientX - bounds.left) / bounds.width) * 100,
      y: ((event.clientY - bounds.top) / bounds.height) * 100,
    };
    setPlayer({
      x: Math.min(92, Math.max(8, nextPlayer.x)),
      y: Math.min(82, Math.max(18, nextPlayer.y)),
    });
    setEaten((current) => {
      const currentSet = new Set(current);
      let newEaten = 0;
      const newlyEatenIds: number[] = [];
      for (const shape of shapes) {
        if (currentSet.has(shape.id)) continue;
        const dx = ((nextPlayer.x - shape.x) / 100) * bounds.width;
        const dy = ((nextPlayer.y - shape.y) / 100) * bounds.height;
        const distance = Math.hypot(dx, dy);
        if (distance < playerSize / 2 + shape.size) {
          currentSet.add(shape.id);
          newlyEatenIds.push(shape.id);
          newEaten += 1;
        }
      }
      if (newEaten > 0) setScore((currentScore) => currentScore + newEaten);
      for (const shapeId of newlyEatenIds) {
        window.setTimeout(() => {
          setEaten((latest) => latest.filter((id) => id !== shapeId));
        }, 360);
      }
      return Array.from(currentSet);
    });
  }

  return (
    <div
      className="relative mb-9 h-40 w-full max-w-md touch-none overflow-visible"
      onPointerMove={moveShapes}
    >
      {shapes.map((shape, index) => {
        const isEaten = eaten.includes(shape.id);
        const commonStyle = {
          left: `${shape.x}%`,
          top: `${shape.y}%`,
          width: shape.size,
          height: shape.size,
          background: shape.kind === "triangle" ? undefined : shape.color,
          animationDelay: `${index * 120}ms`,
        };
        return (
          <span
            key={shape.id}
            className={classNames(
              "pointer-events-none absolute shadow-soft transition-all duration-300",
              shape.kind === "circle" ? "rounded-full" : "rounded-lg",
              shape.kind === "triangle" ? "rounded-none" : "",
              isEaten ? "scale-0 opacity-0" : "scale-100 opacity-100 animate-pulse",
            )}
            style={{
              ...commonStyle,
              clipPath: shape.kind === "triangle" ? "polygon(50% 0%, 0% 100%, 100% 100%)" : undefined,
              background: shape.color,
            }}
          />
        );
      })}
      <div
        className="pointer-events-none absolute rounded-full shadow-[0_18px_45px_rgba(134,45,190,0.22)] transition-[width,height] duration-200"
        style={{
          left: `${player.x}%`,
          top: `${player.y}%`,
          width: playerSize,
          height: playerSize,
          transform: "translate(-50%, -50%)",
          background: "radial-gradient(circle at 34% 28%, rgba(255,255,255,0.9), rgba(156,93,229,0.92) 34%, #862dbe 100%)",
        }}
      />
    </div>
  );
}

function Modal({ title, children, onClose, wide = false }: { title: string; children: ReactNode; onClose: () => void; wide?: boolean }) {
  return (
    <div
      className="fixed inset-y-0 left-0 right-0 z-50 flex items-center justify-center overflow-x-hidden bg-on-surface/20 p-4 backdrop-blur-sm lg:left-72"
      onClick={onClose}
    >
      <section
        className={classNames(
          "glass-card max-h-[90vh] w-full min-w-0 overflow-hidden rounded-[2rem] p-5 shadow-2xl",
          wide ? "max-w-5xl" : "max-w-2xl",
        )}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-5 flex items-center justify-between gap-3">
          <h2 className="min-w-0 truncate font-display text-3xl font-extrabold">{title}</h2>
          <button className="rounded-full bg-white/70 p-3 text-on-surface-variant hover:text-primary" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        {children}
      </section>
    </div>
  );
}

function ConfigureForm({
  mode,
  setMode,
  title,
  setTitle,
  pageNumbers,
  setPageNumbers,
  topK,
  setTopK,
  numberOfQuestions,
  setNumberOfQuestions,
  numberOfOptions,
  setNumberOfOptions,
  difficulty,
  setDifficulty,
  maxSections,
  setMaxSections,
  focusText,
  setFocusText,
  documents,
  selectedDocumentIds,
  onToggle,
  onConfirm,
}: {
  mode: MakerMode;
  setMode: (mode: MakerMode) => void;
  title: string;
  setTitle: (value: string) => void;
  pageNumbers: string;
  setPageNumbers: (value: string) => void;
  topK: number;
  setTopK: (value: number) => void;
  numberOfQuestions: number;
  setNumberOfQuestions: (value: number) => void;
  numberOfOptions: number;
  setNumberOfOptions: (value: number) => void;
  difficulty: string;
  setDifficulty: (value: string) => void;
  maxSections: number;
  setMaxSections: (value: number) => void;
  focusText: string;
  setFocusText: (value: string) => void;
  documents: DocumentSummary[];
  selectedDocumentIds: string[];
  onToggle: (document: DocumentSummary, selected: boolean) => void;
  onConfirm: () => void;
}) {
  return (
    <div className="max-h-[75vh] overflow-auto pr-1">
      <div className="space-y-5">
        <div>
          <p className="mb-2 text-sm font-bold">Output</p>
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: "qcm", label: "QCM", icon: FileQuestion },
              { id: "summary", label: "Summary", icon: BookOpen },
              { id: "mindmap", label: "Mindmap", icon: Network },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className={classNames(
                    "flex min-h-20 flex-col items-center justify-center gap-2 rounded-2xl border text-sm font-extrabold transition",
                    mode === item.id ? "border-primary/50 bg-primary/10 text-primary" : "border-white/70 bg-white/60 text-on-surface-variant",
                  )}
                  onClick={() => setMode(item.id as MakerMode)}
                >
                  <Icon size={20} />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-bold">Sources</p>
          {documents.map((document) => (
            <label key={document.id} className="flex min-w-0 items-center gap-3 rounded-2xl bg-white/60 p-3">
              <input type="checkbox" checked={selectedDocumentIds.includes(document.id)} onChange={(event) => onToggle(document, event.target.checked)} />
              <span className="min-w-0 flex-1 truncate text-sm font-bold">{document.original_filename}</span>
              <span className="text-xs font-bold text-on-surface-variant">{formatBytes(document.file_size)}</span>
            </label>
          ))}
          {documents.length === 0 && <p className="rounded-2xl bg-white/60 p-4 text-sm font-bold text-on-surface-variant">Upload a PDF first.</p>}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Title">
            <input className="form-input" value={title} onChange={(event) => setTitle(event.target.value)} />
          </Field>
          <Field label="Pages a utiliser">
            <input
              className="form-input"
              placeholder="ex: 1,2,5 ou vide"
              value={pageNumbers}
              onBlur={() => setPageNumbers(formatPositiveIntegerList(pageNumbers))}
              onChange={(event) => setPageNumbers(event.target.value)}
            />
          </Field>
          <Field label="Passages consultes par l'IA">
            <input type="number" min={1} max={20} className="form-input" value={topK} onChange={(event) => setTopK(clampInteger(event.target.value, 1, 20))} />
          </Field>

          {mode === "qcm" && (
            <>
              <Field label="Questions">
                <input type="number" min={1} max={60} className="form-input" value={numberOfQuestions} onChange={(event) => setNumberOfQuestions(clampInteger(event.target.value, 1, 60))} />
              </Field>
              <Field label="Choix par question">
                <input type="number" min={2} max={6} className="form-input" value={numberOfOptions} onChange={(event) => setNumberOfOptions(clampInteger(event.target.value, 2, 6))} />
              </Field>
              <Field label="Difficulte">
                <select className="form-input" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                  <option value="expert">Expert</option>
                </select>
              </Field>
            </>
          )}

          {mode === "summary" && (
            <Field label="Sections max">
              <input type="number" min={1} max={10} className="form-input" value={maxSections} onChange={(event) => setMaxSections(clampInteger(event.target.value, 1, 10))} />
            </Field>
          )}
        </div>

        <Field label="Consignes speciales">
          <textarea className="form-input min-h-28 py-3" value={focusText} onChange={(event) => setFocusText(event.target.value)} placeholder="Ex: insiste sur les criteres diagnostiques, evite les questions ambigues." />
        </Field>

        <div className="flex justify-end">
          <Button onClick={onConfirm}>OK</Button>
        </div>
      </div>
    </div>
  );
}

function ExportOptions({
  hasGeneratedMaterial,
  resultQcm,
  resultSummary,
  resultMindmap,
  onExport,
  isBusy,
}: {
  hasGeneratedMaterial: boolean;
  resultQcm: QCM | null;
  resultSummary: Summary | null;
  resultMindmap: MindMap | null;
  onExport: (format: "pdf" | "docx" | "json" | "png" | "mermaid") => void;
  isBusy: boolean;
}) {
  if (!hasGeneratedMaterial) {
    return <p className="rounded-2xl bg-white/70 p-5 text-sm font-bold text-on-surface-variant">Generate material first, then export it.</p>;
  }

  const formats: Array<{ format: "pdf" | "docx" | "json" | "png" | "mermaid"; label: string }> = resultMindmap
    ? [
        { format: "mermaid", label: "Mermaid code" },
      ]
    : [
        { format: "pdf", label: "PDF" },
        { format: "docx", label: "DOCX" },
        { format: "json", label: "JSON" },
      ];

  const title = resultQcm?.title ?? resultSummary?.title ?? resultMindmap?.title ?? "Generated material";

  return (
    <div className="space-y-4">
      <div className="rounded-2xl bg-white/70 p-5">
        <p className="text-sm font-bold text-on-surface-variant">Current material</p>
        <h3 className="mt-1 break-words font-display text-2xl font-extrabold">{title}</h3>
      </div>
      <div className="grid gap-3">
        {formats.map((item) => (
          <button
            key={item.format}
            className="flex min-h-14 items-center justify-between rounded-2xl bg-white/70 px-4 text-left text-sm font-extrabold text-on-surface transition hover:bg-white hover:text-primary"
            onClick={() => onExport(item.format)}
            disabled={isBusy}
          >
            <span>{item.label}</span>
            <Download size={18} />
          </button>
        ))}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block min-w-0">
      <span className="mb-2 block text-sm font-bold">{label}</span>
      {children}
    </label>
  );
}

function clampInteger(value: string, min: number, max: number): number {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return min;
  return Math.min(max, Math.max(min, parsed));
}

function parsePositiveIntegerList(value: string): number[] {
  return value
    .split(",")
    .map((item) => Number.parseInt(item.trim(), 10))
    .filter((item) => Number.isInteger(item) && item > 0);
}

function formatPositiveIntegerList(value: string): string {
  return parsePositiveIntegerList(value).join(", ");
}
