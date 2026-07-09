export const env = {
  authBaseUrl: import.meta.env.VITE_AUTH_SERVICE_URL ?? "http://localhost:8001",
  userBaseUrl: import.meta.env.VITE_USER_SERVICE_URL ?? "http://localhost:8002",
  documentBaseUrl: import.meta.env.VITE_DOCUMENT_SERVICE_URL ?? "http://localhost:8003",
  knowledgeBaseUrl: import.meta.env.VITE_KNOWLEDGE_SERVICE_URL ?? "http://localhost:8004",
  aiBaseUrl: import.meta.env.VITE_AI_SERVICE_URL ?? "http://localhost:8005",
  generationBaseUrl: import.meta.env.VITE_GENERATION_SERVICE_URL ?? "http://localhost:8006",
  evaluationBaseUrl: import.meta.env.VITE_EVALUATION_SERVICE_URL ?? "http://localhost:8007",
  learningBaseUrl: import.meta.env.VITE_LEARNING_SERVICE_URL ?? "http://localhost:8008",
  exportBaseUrl: import.meta.env.VITE_EXPORT_SERVICE_URL ?? "http://localhost:8009",
};
