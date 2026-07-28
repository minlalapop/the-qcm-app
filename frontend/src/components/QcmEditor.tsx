import { CheckCircle2, Download, Pencil, Save, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { useAuth } from "../auth/AuthProvider";
import { deleteQuestion, updateQcm, updateQuestion } from "../api/generation";
import type { DocumentSummary, QCM, Question } from "../api/types";
import { Button } from "./Button";

export function QcmEditor({
  qcm,
  documents = [],
  onOpenSource,
  onChange,
  onExport,
}: {
  qcm: QCM;
  documents?: DocumentSummary[];
  onOpenSource?: (documentId: string) => void;
  onChange: (qcm: QCM) => void;
  onExport?: (format: "pdf" | "docx" | "xlsx") => void;
}) {
  const { accessToken } = useAuth();
  const [title, setTitle] = useState(qcm.title);
  const [status, setStatus] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const documentById = useMemo(() => new Map(documents.map((document) => [document.id, document])), [documents]);

  useEffect(() => {
    setTitle(qcm.title);
    setIsEditing(false);
  }, [qcm.id, qcm.title]);

  async function saveAll() {
    if (!accessToken || !isEditing) return;
    setStatus("Saving QCM...");
    const updatedQcm = await updateQcm(accessToken, qcm.id, { title });
    const updatedQuestions = [];
    for (const question of qcm.questions) {
      updatedQuestions.push(
        await updateQuestion(accessToken, qcm.id, question.id, {
          question_text: question.question_text,
          explanation: question.explanation,
          difficulty: question.difficulty,
          answers: question.answers
            .slice()
            .sort((a, b) => a.order_index - b.order_index)
            .map((answer) => ({
              label: answer.label,
              answer_text: answer.answer_text,
              is_correct: answer.is_correct,
              order_index: answer.order_index,
            })),
        }),
      );
    }
    onChange({ ...updatedQcm, questions: updatedQuestions });
    setIsEditing(false);
    setStatus("QCM saved");
  }

  async function removeQuestion(questionId: string) {
    if (!accessToken || !isEditing) return;
    setStatus("Deleting question...");
    await deleteQuestion(accessToken, qcm.id, questionId);
    onChange({ ...qcm, questions: qcm.questions.filter((question) => question.id !== questionId) });
    setStatus("Question deleted");
  }

  function patchQuestion(questionId: string, updater: (question: Question) => Question) {
    onChange({
      ...qcm,
      questions: qcm.questions.map((question) => (question.id === questionId ? updater(question) : question)),
    });
  }

  return (
    <section className="glass-card min-w-0 overflow-x-hidden rounded-[2rem] p-6">
      <div className="mb-6 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0 flex-1">
          <label className="mb-2 block text-xs font-extrabold uppercase tracking-[0.14em] text-on-surface-variant">
            QCM title
          </label>
          <input
            className="h-12 w-full min-w-0 rounded-2xl border border-outline-variant bg-white/70 px-4 font-display text-xl font-bold outline-none focus:border-primary focus:ring-4 focus:ring-primary/10"
            value={title}
            disabled={!isEditing}
            onChange={(event) => setTitle(event.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {onExport && (
            <>
              <Button variant="ghost" onClick={() => onExport("pdf")}>
                <Download size={17} />
                PDF
              </Button>
              <Button variant="ghost" onClick={() => onExport("docx")}>DOCX</Button>
              <Button variant="ghost" onClick={() => onExport("xlsx")}>Excel</Button>
            </>
          )}
        </div>
      </div>

      {status && <p className="mb-4 rounded-2xl bg-primary/10 px-4 py-3 text-sm font-bold text-primary">{status}</p>}

      <div className="space-y-5">
        {qcm.questions.map((question, questionIndex) => (
          <article key={question.id} className="min-w-0 overflow-hidden rounded-[1.5rem] border border-white/70 bg-white/55 p-5">
            <div className="mb-4 flex items-start justify-between gap-3">
              <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-extrabold text-primary">
                Question {questionIndex + 1}
              </span>
              <button
                className="rounded-full p-2 text-on-surface-variant transition hover:bg-error-container hover:text-error"
                disabled={!isEditing}
                onClick={() => removeQuestion(question.id)}
              >
                <Trash2 size={17} />
              </button>
            </div>

            <textarea
              className="min-h-24 w-full min-w-0 rounded-2xl border border-outline-variant bg-white/80 p-4 font-semibold outline-none focus:border-primary focus:ring-4 focus:ring-primary/10"
              value={question.question_text}
              disabled={!isEditing}
              onChange={(event) => patchQuestion(question.id, (item) => ({ ...item, question_text: event.target.value }))}
            />

            <div className="mt-4 grid gap-3">
              {question.answers
                .slice()
                .sort((a, b) => a.order_index - b.order_index)
                .map((answer) => (
                  <div key={answer.id} className="grid min-w-0 gap-3 rounded-2xl bg-white/70 p-3 sm:grid-cols-[72px_minmax(0,1fr)_120px]">
                    <span className="flex h-11 min-w-0 items-center justify-center rounded-xl border border-outline-variant bg-surface-container text-sm font-extrabold text-on-surface-variant">
                      {answer.label}
                    </span>
                    <input
                      className="h-11 min-w-0 rounded-xl border border-outline-variant bg-white px-3 text-sm outline-none"
                      value={answer.answer_text}
                      disabled={!isEditing}
                      onChange={(event) =>
                        patchQuestion(question.id, (item) => ({
                          ...item,
                          answers: item.answers.map((candidate) =>
                            candidate.id === answer.id ? { ...candidate, answer_text: event.target.value } : candidate,
                          ),
                        }))
                      }
                    />
                    <button
                      className={`flex h-11 items-center justify-center gap-2 rounded-xl text-sm font-bold transition ${
                        answer.is_correct ? "bg-primary text-white" : "bg-surface-container text-on-surface-variant"
                      }`}
                      disabled={!isEditing}
                      onClick={() =>
                        patchQuestion(question.id, (item) => ({
                          ...item,
                          answers: item.answers.map((candidate) => ({
                            ...candidate,
                            is_correct: candidate.id === answer.id,
                            is_distractor: candidate.id !== answer.id,
                          })),
                        }))
                      }
                    >
                      {answer.is_correct && <CheckCircle2 size={16} />}
                      Correct
                    </button>
                  </div>
                ))}
            </div>

            <label className="mt-4 block">
              <span className="mb-2 block text-xs font-extrabold uppercase tracking-[0.14em] text-on-surface-variant">
                Explanation
              </span>
              <textarea
                className="min-h-20 w-full min-w-0 rounded-2xl border border-outline-variant bg-white/80 p-4 outline-none focus:border-primary focus:ring-4 focus:ring-primary/10"
                value={question.explanation ?? ""}
                disabled={!isEditing}
                onChange={(event) => patchQuestion(question.id, (item) => ({ ...item, explanation: event.target.value }))}
              />
            </label>

            <QuestionSource question={question} documentById={documentById} onOpenSource={onOpenSource} />
          </article>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap justify-end gap-2">
        <Button variant="ghost" onClick={() => setIsEditing(true)} disabled={isEditing}>
          <Pencil size={17} />
          Modify
        </Button>
        <Button variant="secondary" onClick={saveAll} disabled={!isEditing}>
          <Save size={17} />
          Save QCM
        </Button>
      </div>
    </section>
  );
}

function QuestionSource({
  question,
  documentById,
  onOpenSource,
}: {
  question: Question;
  documentById: Map<string, DocumentSummary>;
  onOpenSource?: (documentId: string) => void;
}) {
  const sourceDocument = question.source_document_id ? documentById.get(question.source_document_id) : null;
  const sourceParts = [question.source_page ? `page ${question.source_page}` : null, question.citation || null].filter(Boolean);

  return (
    <div className="mt-4 min-w-0 rounded-2xl bg-white/50 px-4 py-3 text-xs font-semibold text-on-surface-variant">
      <span>Source: </span>
      {sourceDocument && onOpenSource ? (
        <button
          className="max-w-full break-words font-extrabold text-primary underline-offset-4 hover:underline"
          onClick={() => onOpenSource(sourceDocument.id)}
        >
          {sourceDocument.original_filename}
        </button>
      ) : (
        <span className="font-extrabold">{sourceDocument?.original_filename ?? "selected document"}</span>
      )}
      {sourceParts.length > 0 && <span> - {sourceParts.join(" - ")}</span>}
    </div>
  );
}
