import { apiRequest } from "./http";
import { env } from "../env";
import type { Answer, MindMap, QCM, Question, SourceSelection, Summary } from "./types";

export type GenerateQcmPayload = {
  title: string;
  source_selection: SourceSelection;
  number_of_questions: number;
  number_of_options: number;
  difficulty: string;
  top_k: number;
  temperature: number;
  max_tokens: number;
  duplication_check: boolean;
  custom_rules: Record<string, unknown>;
};

export type GenerateSummaryPayload = {
  title: string;
  source_selection: SourceSelection;
  style: string;
  max_sections: number;
  top_k: number;
  temperature: number;
  max_tokens: number;
  custom_rules: Record<string, unknown>;
};

export type GenerateMindMapPayload = {
  title: string;
  source_selection: SourceSelection;
  output_format: "mermaid" | "json";
  top_k: number;
  temperature: number;
  max_tokens: number;
  custom_rules: Record<string, unknown>;
};

export function listQcms(token: string): Promise<QCM[]> {
  return apiRequest<QCM[]>(env.generationBaseUrl, "/generation/qcms", { token });
}

export function getQcm(token: string, qcmId: string): Promise<QCM> {
  return apiRequest<QCM>(env.generationBaseUrl, `/generation/qcms/${qcmId}`, { token });
}

export function generateQcm(token: string, payload: GenerateQcmPayload): Promise<QCM> {
  return apiRequest<QCM>(env.generationBaseUrl, "/generation/qcms", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function updateQcm(token: string, qcmId: string, payload: Partial<Pick<QCM, "title" | "status" | "difficulty">>): Promise<QCM> {
  return apiRequest<QCM>(env.generationBaseUrl, `/generation/qcms/${qcmId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function deleteQcm(token: string, qcmId: string): Promise<void> {
  return apiRequest<void>(env.generationBaseUrl, `/generation/qcms/${qcmId}`, {
    method: "DELETE",
    token,
  });
}

export function updateQuestion(
  token: string,
  qcmId: string,
  questionId: string,
  payload: {
    question_text?: string;
    explanation?: string | null;
    difficulty?: string | null;
    answers?: Array<Pick<Answer, "label" | "answer_text" | "is_correct" | "order_index">>;
  },
): Promise<Question> {
  return apiRequest<Question>(env.generationBaseUrl, `/generation/qcms/${qcmId}/questions/${questionId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function deleteQuestion(token: string, qcmId: string, questionId: string): Promise<void> {
  return apiRequest<void>(env.generationBaseUrl, `/generation/qcms/${qcmId}/questions/${questionId}`, {
    method: "DELETE",
    token,
  });
}

export function listSummaries(token: string): Promise<Summary[]> {
  return apiRequest<Summary[]>(env.generationBaseUrl, "/generation/summaries", { token });
}

export function generateSummary(token: string, payload: GenerateSummaryPayload): Promise<Summary> {
  return apiRequest<Summary>(env.generationBaseUrl, "/generation/summaries", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function updateSummary(token: string, summaryId: string, payload: Partial<Pick<Summary, "title">>): Promise<Summary> {
  return apiRequest<Summary>(env.generationBaseUrl, `/generation/summaries/${summaryId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}

export function listMindmaps(token: string): Promise<MindMap[]> {
  return apiRequest<MindMap[]>(env.generationBaseUrl, "/generation/mindmaps", { token });
}

export function generateMindmap(token: string, payload: GenerateMindMapPayload): Promise<MindMap> {
  return apiRequest<MindMap>(env.generationBaseUrl, "/generation/mindmaps", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function updateMindmap(token: string, mindmapId: string, payload: Partial<Pick<MindMap, "title">>): Promise<MindMap> {
  return apiRequest<MindMap>(env.generationBaseUrl, `/generation/mindmaps/${mindmapId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(payload),
  });
}
