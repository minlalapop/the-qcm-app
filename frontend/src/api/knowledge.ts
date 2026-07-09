import { apiRequest } from "./http";
import { env } from "../env";
import type { KnowledgeIndex } from "./types";

export function indexDocument(token: string, documentId: string, forceReindex = false): Promise<KnowledgeIndex> {
  return apiRequest<KnowledgeIndex>(env.knowledgeBaseUrl, `/knowledge/documents/${documentId}/index`, {
    method: "POST",
    token,
    body: JSON.stringify({ force_reindex: forceReindex }),
  });
}

export function listIndexes(token: string): Promise<KnowledgeIndex[]> {
  return apiRequest<KnowledgeIndex[]>(env.knowledgeBaseUrl, "/knowledge/indexes", { token });
}
