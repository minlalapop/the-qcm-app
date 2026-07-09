import { ApiError, apiRequest } from "./http";
import { env } from "../env";
import type { DocumentPage, DocumentSummary } from "./types";

export type DocumentPageImage = {
  page_number: number;
  image_url: string;
};

export function listDocuments(token: string): Promise<DocumentSummary[]> {
  return apiRequest<DocumentSummary[]>(env.documentBaseUrl, "/documents", { token });
}

export function uploadDocument(token: string, file: File): Promise<DocumentSummary> {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<DocumentSummary>(env.documentBaseUrl, "/documents/upload", {
    method: "POST",
    token,
    body: formData,
  });
}

export function deleteDocument(token: string, documentId: string): Promise<void> {
  return apiRequest<void>(env.documentBaseUrl, `/documents/${documentId}`, {
    method: "DELETE",
    token,
  });
}

export function listDocumentPages(token: string, documentId: string): Promise<DocumentPage[]> {
  return apiRequest<DocumentPage[]>(env.documentBaseUrl, `/documents/${documentId}/pages`, { token });
}

export async function getDocumentPdfBlob(token: string, documentId: string): Promise<Blob> {
  const response = await fetch(`${env.documentBaseUrl}/documents/${documentId}/file`, {
    headers: {
      Accept: "application/pdf",
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new ApiError(detail || "Could not load PDF preview", response.status, detail);
  }

  return response.blob();
}

export async function getDocumentPageImageUrls(token: string, documentId: string): Promise<Array<{ pageNumber: number; url: string }>> {
  const pages = await apiRequest<DocumentPageImage[]>(env.documentBaseUrl, `/documents/${documentId}/page-images`, { token });
  const urls = await Promise.all(
    pages.map(async (page) => {
      const response = await fetch(`${env.documentBaseUrl}${page.image_url}`, {
        headers: {
          Accept: "image/png",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new ApiError(detail || "Could not load PDF page preview", response.status, detail);
      }

      return { pageNumber: page.page_number, url: URL.createObjectURL(await response.blob()) };
    }),
  );
  return urls;
}
