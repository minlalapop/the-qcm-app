import { apiRequest } from "./http";
import { env } from "../env";
import type { Evaluation, QualityMetric, QuestionFeedback } from "./types";

export type CreateEvaluationPayload = {
  rating: number;
  quality_score?: number | null;
  difficulty_score?: number | null;
  hallucination_score?: number | null;
  validation_status: "approved" | "rejected" | "needs_revision" | "needs_review";
  is_validated_for_learning: boolean;
  comment?: string | null;
  metadata_payload?: Record<string, unknown>;
};

export type CreateQuestionFeedbackPayload = {
  rating?: number | null;
  question_is_correct?: boolean | null;
  correct_answer_is_valid?: boolean | null;
  distractors_quality?: "too_easy" | "plausible" | "confusing" | "invalid" | null;
  is_ambiguous?: boolean;
  difficulty_fit?: "too_easy" | "adapted" | "too_hard" | "wrong_level" | null;
  issue_types?: string[];
  comment?: string | null;
  corrected_question_text?: string | null;
  is_validated_example?: boolean;
  learning_payload?: Record<string, unknown>;
};

export function listReviews(token: string): Promise<Evaluation[]> {
  return apiRequest<Evaluation[]>(env.evaluationBaseUrl, "/evaluation/reviews", { token });
}

export function getQcmMetrics(token: string, qcmId: string): Promise<QualityMetric> {
  return apiRequest<QualityMetric>(env.evaluationBaseUrl, `/evaluation/qcms/${qcmId}/metrics`, { token });
}

export function createQcmReview(token: string, qcmId: string, payload: CreateEvaluationPayload): Promise<Evaluation> {
  return apiRequest<Evaluation>(env.evaluationBaseUrl, `/evaluation/qcms/${qcmId}/reviews`, {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function createQuestionFeedback(
  token: string,
  qcmId: string,
  questionId: string,
  payload: CreateQuestionFeedbackPayload,
): Promise<QuestionFeedback> {
  return apiRequest<QuestionFeedback>(env.evaluationBaseUrl, `/evaluation/qcms/${qcmId}/questions/${questionId}/feedback`, {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}
