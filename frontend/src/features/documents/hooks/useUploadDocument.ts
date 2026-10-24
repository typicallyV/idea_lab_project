"use client";

import { useCallback, useRef, useState } from "react";
import { getDocumentStatus, uploadDocument } from "@/features/documents/api";
import type { DocumentStatusPayload } from "@/types/document";

const POLL_INTERVAL_MS = 2000;

export function useUploadDocument() {
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<DocumentStatusPayload | null>(null);
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearTimeout(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    stopPolling();
    setProgress(0);
    setStatusMessage("");
    setUploading(false);
    setUploaded(false);
    setError("");
    setResult(null);
  }, [stopPolling]);

  const upload = useCallback(
    async (file: File) => {
      reset();
      setUploading(true);
      setProgress(5);
      setStatusMessage("Uploading document...");

      try {
        const { documentId, filename } = await uploadDocument(file);
        console.log("[upload] started", documentId, filename);

        let transientFailures = 0;
        const pollStatus = async () => {
          try {
            const status = await getDocumentStatus(documentId);
            transientFailures = 0;
            console.log("[upload] status", status.status, status.progress + "%");
            setProgress(status.progress);
            setStatusMessage(status.statusMessage);

            if (status.status === "completed") {
              stopPolling();
              setProgress(100);
              setUploading(false);
              setUploaded(true);
              setResult(status);
            } else if (status.status === "failed") {
              stopPolling();
              setUploading(false);
              setError(status.error || "Processing failed");
            } else {
              pollRef.current = setTimeout(pollStatus, POLL_INTERVAL_MS);
            }
          } catch (pollErr) {
            transientFailures += 1;
            if (transientFailures <= 4) {
              setStatusMessage("Connection hiccup. Retrying document status...");
              pollRef.current = setTimeout(pollStatus, POLL_INTERVAL_MS * transientFailures);
            } else {
              stopPolling();
              setUploading(false);
              setError(pollErr instanceof Error ? pollErr.message : "Status polling error");
            }
          }
        };
        pollRef.current = setTimeout(pollStatus, POLL_INTERVAL_MS);
      } catch (err) {
        console.error("[upload] failed", err);
        setUploading(false);
        setError(err instanceof Error ? err.message : "Failed to upload document");
      }
    },
    [reset, stopPolling],
  );

  return { upload, reset, progress, statusMessage, uploading, uploaded, error, result };
}
