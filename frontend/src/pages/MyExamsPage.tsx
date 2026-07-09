import { Download, FileQuestion, RefreshCw, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { createQcmReview, createQuestionFeedback } from "../api/evaluation";
import { downloadExport, exportQcm } from "../api/exports";
import { deleteQcm, listQcms } from "../api/generation";
import type { QCM } from "../api/types";
import { useAuth } from "../auth/AuthProvider";
import { Button } from "../components/Button";
import { QcmEditor } from "../components/QcmEditor";
import { classNames, formatDate } from "../utils/format";

export function MyExamsPage() {
  const { accessToken } = useAuth();
  const [qcms, setQcms] = useState<QCM[]>([]);
  const [selectedQcm, setSelectedQcm] = useState<QCM | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void refresh();
  }, [accessToken]);

  async function refresh() {
    if (!accessToken) return;
    const data = await listQcms(accessToken);
    setQcms(data);
    setSelectedQcm((current) => current ?? data[0] ?? null);
  }

  async function removeQcm(qcmId: string) {
    if (!accessToken) return;
    await deleteQcm(accessToken, qcmId);
    setQcms((current) => current.filter((qcm) => qcm.id !== qcmId));
    if (selectedQcm?.id === qcmId) setSelectedQcm(null);
  }

  async function exportSelected(format: "pdf" | "docx" | "json") {
    if (!accessToken || !selectedQcm) return;
    setError(null);
    setStatus(`Exporting ${format.toUpperCase()}...`);
    try {
      const record = await exportQcm(accessToken, selectedQcm.id, format);
      await downloadExport(accessToken, record.id, `${selectedQcm.title}.${format}`);
      setStatus("Export downloaded");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    }
  }

  function updateSelected(updated: QCM) {
    setSelectedQcm(updated);
    setQcms((current) => current.map((qcm) => (qcm.id === updated.id ? updated : qcm)));
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[380px_1fr]">
      <aside className="glass-card rounded-[2rem] p-5">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="font-display text-2xl font-bold">My Exams</h2>
            <p className="text-sm text-on-surface-variant">{qcms.length} generated QCM(s)</p>
          </div>
          <button className="text-primary" onClick={refresh}>
            <RefreshCw size={18} />
          </button>
        </div>

        <div className="space-y-3">
          {qcms.map((qcm) => (
            <article
              key={qcm.id}
              className={classNames(
                "rounded-2xl border p-4 transition",
                selectedQcm?.id === qcm.id ? "border-primary/40 bg-primary/10" : "border-white/70 bg-white/55",
              )}
            >
              <button className="w-full text-left" onClick={() => setSelectedQcm(qcm)}>
                <div className="flex gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <FileQuestion size={20} />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-bold">{qcm.title}</p>
                    <p className="text-xs text-on-surface-variant">
                      {qcm.questions.length} questions | {formatDate(qcm.created_at)}
                    </p>
                    <p className="mt-1 text-xs font-bold text-primary">{qcm.difficulty}</p>
                  </div>
                </div>
              </button>
              <button className="mt-3 flex items-center gap-2 text-xs font-bold text-error" onClick={() => removeQcm(qcm.id)}>
                <Trash2 size={14} />
                Delete
              </button>
            </article>
          ))}
          {qcms.length === 0 && <p className="text-sm text-on-surface-variant">No QCM generated yet.</p>}
        </div>
      </aside>

      <main className="space-y-6">
        <section className="glass-card rounded-[2rem] p-5">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="font-display text-3xl font-extrabold">Exam correction workspace</h1>
              <p className="mt-1 text-on-surface-variant">
                Review correct answers, edit questions, delete weak items, then export the final exam.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => exportSelected("pdf")} disabled={!selectedQcm}>
                <Download size={17} />
                PDF
              </Button>
              <Button variant="ghost" onClick={() => exportSelected("docx")} disabled={!selectedQcm}>DOCX</Button>
              <Button variant="ghost" onClick={() => exportSelected("json")} disabled={!selectedQcm}>JSON</Button>
            </div>
          </div>
          {status && <p className="mt-4 rounded-2xl bg-primary/10 px-4 py-3 text-sm font-bold text-primary">{status}</p>}
          {error && <p className="mt-4 rounded-2xl bg-error-container px-4 py-3 text-sm font-bold text-error">{error}</p>}
        </section>

        {selectedQcm ? (
          <>
            <TeacherFeedbackPanel qcm={selectedQcm} onSaved={(message) => setStatus(message)} />
            <QcmEditor qcm={selectedQcm} onChange={updateSelected} onExport={exportSelected} />
          </>
        ) : (
          <section className="glass-card rounded-[2rem] p-10 text-center text-on-surface-variant">
            Select a QCM to review.
          </section>
        )}
      </main>
    </div>
  );
}

function TeacherFeedbackPanel({ qcm, onSaved }: { qcm: QCM; onSaved: (message: string) => void }) {
  const { accessToken } = useAuth();
  const [rating, setRating] = useState(4);
  const [validationStatus, setValidationStatus] = useState<"approved" | "rejected" | "needs_revision" | "needs_review">("needs_review");
  const [reviewComment, setReviewComment] = useState("");
  const [validatedForLearning, setValidatedForLearning] = useState(false);
  const [selectedQuestionId, setSelectedQuestionId] = useState(qcm.questions[0]?.id ?? "");
  const [questionRating, setQuestionRating] = useState(4);
  const [questionIssue, setQuestionIssue] = useState("none");
  const [questionComment, setQuestionComment] = useState("");
  const [correctedQuestion, setCorrectedQuestion] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    setSelectedQuestionId(qcm.questions[0]?.id ?? "");
  }, [qcm.id, qcm.questions]);

  async function saveReview() {
    if (!accessToken) return;
    setLocalError(null);
    setIsSaving(true);
    try {
      await createQcmReview(accessToken, qcm.id, {
        rating,
        validation_status: validationStatus,
        is_validated_for_learning: validatedForLearning,
        comment: reviewComment || null,
        metadata_payload: { source: "teacher_feedback_panel" },
      });
      setReviewComment("");
      onSaved("Teacher review saved");
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : "Could not save review");
    } finally {
      setIsSaving(false);
    }
  }

  async function saveQuestionFeedback() {
    if (!accessToken || !selectedQuestionId) return;
    setLocalError(null);
    setIsSaving(true);
    try {
      const issueTypes = questionIssue === "none" ? [] : [questionIssue];
      await createQuestionFeedback(accessToken, qcm.id, selectedQuestionId, {
        rating: questionRating,
        question_is_correct: questionIssue === "incorrect_question" ? false : null,
        correct_answer_is_valid: questionIssue === "incorrect_answer" ? false : null,
        distractors_quality: questionIssue === "weak_distractors" ? "too_easy" : null,
        is_ambiguous: questionIssue === "ambiguous",
        difficulty_fit: questionIssue === "wrong_difficulty" ? "wrong_level" : null,
        issue_types: issueTypes,
        comment: questionComment || null,
        corrected_question_text: correctedQuestion || null,
        is_validated_example: Boolean(correctedQuestion.trim()),
        learning_payload: { source: "teacher_feedback_panel" },
      });
      setQuestionComment("");
      setCorrectedQuestion("");
      onSaved("Question feedback saved for Learning Service");
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : "Could not save question feedback");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="glass-card rounded-[2rem] p-5">
      <div className="mb-5">
        <h2 className="font-display text-2xl font-bold">Teacher feedback</h2>
        <p className="mt-1 text-sm text-on-surface-variant">
          These reviews are stored by Evaluation Service and reused by Learning Service.
        </p>
      </div>

      {localError && <p className="mb-4 rounded-2xl bg-error-container px-4 py-3 text-sm font-bold text-error">{localError}</p>}

      <div className="grid gap-5 xl:grid-cols-2">
        <div className="rounded-2xl bg-white/60 p-4">
          <h3 className="font-bold">Global QCM review</h3>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-sm font-bold">Rating</span>
              <input className="form-input" type="number" min={1} max={5} value={rating} onChange={(event) => setRating(clamp(event.target.value, 1, 5))} />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-bold">Validation</span>
              <select className="form-input" value={validationStatus} onChange={(event) => setValidationStatus(event.target.value as typeof validationStatus)}>
                <option value="needs_review">Needs review</option>
                <option value="approved">Approved</option>
                <option value="needs_revision">Needs revision</option>
                <option value="rejected">Rejected</option>
              </select>
            </label>
          </div>
          <label className="mt-3 flex items-center gap-2 text-sm font-bold">
            <input type="checkbox" checked={validatedForLearning} onChange={(event) => setValidatedForLearning(event.target.checked)} />
            Validated for learning
          </label>
          <textarea
            className="form-input mt-3 min-h-24 py-3"
            value={reviewComment}
            onChange={(event) => setReviewComment(event.target.value)}
            placeholder="Global feedback for this QCM."
          />
          <Button className="mt-3" variant="secondary" onClick={saveReview} disabled={isSaving}>
            Save review
          </Button>
        </div>

        <div className="rounded-2xl bg-white/60 p-4">
          <h3 className="font-bold">Question feedback</h3>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-sm font-bold">Question</span>
              <select className="form-input" value={selectedQuestionId} onChange={(event) => setSelectedQuestionId(event.target.value)}>
                {qcm.questions.map((question, index) => (
                  <option key={question.id} value={question.id}>
                    Question {index + 1}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-2 block text-sm font-bold">Rating</span>
              <input className="form-input" type="number" min={1} max={5} value={questionRating} onChange={(event) => setQuestionRating(clamp(event.target.value, 1, 5))} />
            </label>
            <label className="block sm:col-span-2">
              <span className="mb-2 block text-sm font-bold">Issue</span>
              <select className="form-input" value={questionIssue} onChange={(event) => setQuestionIssue(event.target.value)}>
                <option value="none">No specific issue</option>
                <option value="incorrect_question">Question incorrecte</option>
                <option value="incorrect_answer">Reponse incorrecte</option>
                <option value="weak_distractors">Distracteurs trop faciles</option>
                <option value="ambiguous">Question ambigue</option>
                <option value="wrong_difficulty">Difficulte mal adaptee</option>
              </select>
            </label>
          </div>
          <textarea
            className="form-input mt-3 min-h-20 py-3"
            value={questionComment}
            onChange={(event) => setQuestionComment(event.target.value)}
            placeholder="Commentaire du prof."
          />
          <textarea
            className="form-input mt-3 min-h-20 py-3"
            value={correctedQuestion}
            onChange={(event) => setCorrectedQuestion(event.target.value)}
            placeholder="Version corrigee de la question, optionnel."
          />
          <Button className="mt-3" variant="secondary" onClick={saveQuestionFeedback} disabled={isSaving || !selectedQuestionId}>
            Save question feedback
          </Button>
        </div>
      </div>
    </section>
  );
}

function clamp(value: string, min: number, max: number): number {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return min;
  return Math.min(max, Math.max(min, parsed));
}
