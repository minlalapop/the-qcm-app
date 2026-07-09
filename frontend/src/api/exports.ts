import { apiRequest } from "./http";
import { env } from "../env";
import type { ExportJob, ExportRecord } from "./types";

export type ExportFormat = "pdf" | "docx" | "json" | "png" | "mermaid";

export function listExports(token: string): Promise<ExportRecord[]> {
  return apiRequest<ExportRecord[]>(env.exportBaseUrl, "/exports", { token });
}

export function listExportJobs(token: string): Promise<ExportJob[]> {
  return apiRequest<ExportJob[]>(env.exportBaseUrl, "/exports/jobs", { token });
}

export function exportQcm(token: string, qcmId: string, format: "pdf" | "docx" | "json"): Promise<ExportRecord> {
  return apiRequest<ExportRecord>(env.exportBaseUrl, `/exports/qcms/${qcmId}/${format}`, {
    method: "POST",
    token,
    body: JSON.stringify({ include_answers: true, include_explanations: true, include_sources: true }),
  });
}

export function exportMindmap(token: string, mindmapId: string, format: "png" | "mermaid" | "json"): Promise<ExportRecord> {
  return apiRequest<ExportRecord>(env.exportBaseUrl, `/exports/mindmaps/${mindmapId}/${format}`, {
    method: "POST",
    token,
    body: JSON.stringify({ include_sources: true }),
  });
}

export function exportSummary(token: string, summaryId: string, format: "pdf" | "docx" | "json"): Promise<ExportRecord> {
  return apiRequest<ExportRecord>(env.exportBaseUrl, `/exports/summaries/${summaryId}/${format}`, {
    method: "POST",
    token,
    body: JSON.stringify({ include_sources: true }),
  });
}

export async function downloadExport(token: string, exportId: string, filename: string): Promise<void> {
  const response = await fetch(`${env.exportBaseUrl}/exports/${exportId}/download`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Could not download export");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
