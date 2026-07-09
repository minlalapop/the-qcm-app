export type DocumentSummary = {
  id: string;
  owner_id: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  pdf_hash: string;
  status: string;
  page_count: number;
  created_at: string;
  updated_at: string;
};

export type DocumentPage = {
  id: string;
  page_number: number;
  text_content: string;
};

export type KnowledgeIndex = {
  id: string;
  document_id: string;
  chunks_count: number;
  status: string;
  created_at: string;
  updated_at: string;
};

export type SourceSelection = {
  document_ids: string[];
  page_numbers: number[];
  chunk_ids: string[];
  focus_text?: string | null;
};

export type Answer = {
  id: string;
  label: string;
  answer_text: string;
  is_correct: boolean;
  is_distractor: boolean;
  order_index: number;
};

export type Question = {
  id: string;
  order_index: number;
  question_text: string;
  explanation: string | null;
  difficulty: string | null;
  source_document_id: string | null;
  source_page: number | null;
  source_chunk_id: string | null;
  citation: string | null;
  answers: Answer[];
};

export type QCM = {
  id: string;
  owner_id: string;
  title: string;
  document_ids: string[];
  status: string;
  difficulty: string;
  source_selection: Record<string, unknown>;
  ai_request_ids: string[];
  questions: Question[];
  created_at: string;
  updated_at: string;
};

export type Summary = {
  id: string;
  owner_id: string;
  title: string;
  document_ids: string[];
  content: string;
  structured_payload: Record<string, unknown>;
  source_selection: Record<string, unknown>;
  ai_request_ids: string[];
  created_at: string;
};

export type MindMap = {
  id: string;
  owner_id: string;
  title: string;
  document_ids: string[];
  output_format: string;
  mermaid_content: string | null;
  json_content: Record<string, unknown>;
  source_selection: Record<string, unknown>;
  ai_request_ids: string[];
  created_at: string;
};

export type ExportRecord = {
  id: string;
  owner_id: string;
  resource_type: string;
  resource_id: string;
  export_format: string;
  title: string;
  file_path: string;
  mime_type: string;
  status: string;
  created_at: string;
};

export type ExportJob = {
  id: string;
  export_id: string | null;
  resource_type: string;
  resource_id: string;
  export_format: string;
  status: string;
  error_message: string | null;
  created_at: string;
};

export type Evaluation = {
  id: string;
  qcm_id: string;
  reviewer_id: string;
  reviewer_role: string;
  rating: number;
  quality_score: number | null;
  difficulty_score: number | null;
  hallucination_score: number | null;
  validation_status: string;
  is_validated_for_learning: boolean;
  comment: string | null;
  metadata_payload: Record<string, unknown>;
  created_at: string;
};

export type QuestionFeedback = {
  id: string;
  qcm_id: string;
  question_id: string;
  reviewer_id: string;
  reviewer_role: string;
  rating: number | null;
  question_is_correct: boolean | null;
  correct_answer_is_valid: boolean | null;
  distractors_quality: string | null;
  distractors_score: number | null;
  is_ambiguous: boolean;
  difficulty_fit: string | null;
  difficulty_score: number | null;
  issue_types: string[];
  comment: string | null;
  corrected_question_text: string | null;
  corrected_answers: Array<Record<string, unknown>>;
  is_validated_example: boolean;
  learning_payload: Record<string, unknown>;
  created_at: string;
};

export type QualityMetric = {
  qcm_id: string;
  feedback_count: number;
  review_count: number;
  average_rating: number | null;
  quality_score: number | null;
  difficulty_score: number | null;
  hallucination_score: number | null;
  incorrect_questions_count: number;
  ambiguous_questions_count: number;
  weak_distractors_count: number;
  hallucination_reports_count: number;
};
