import { apiClient } from "@/lib/api-client";
import { unwrap } from "@/lib/api-envelope";
import type { ChatResponse } from "@/types/chat";

/**
 * Send an optional answer-language preference through the API gateway to RAG.
 */
export async function askDocument(
  documentId: string,
  question: string,
  responseLanguage: "auto" | "hi" = "auto",
): Promise<ChatResponse> {
  const res = await apiClient.post("/api/chat/chat", {
    document_id: documentId,
    question,
    response_language: responseLanguage,
  });
  return unwrap(res);
}
