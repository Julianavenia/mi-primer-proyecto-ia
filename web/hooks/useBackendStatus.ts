"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";

export type BackendStatus =
  | { state: "loading" }
  | { state: "online"; llmBackend: string }
  | { state: "offline" };

/** Comprueba /health al montar, para avisar cuanto antes si el backend no responde. */
export function useBackendStatus(): BackendStatus {
  const [status, setStatus] = useState<BackendStatus>({ state: "loading" });

  useEffect(() => {
    let cancelled = false;

    getHealth()
      .then((health) => {
        if (!cancelled) setStatus({ state: "online", llmBackend: health.llm_backend });
      })
      .catch(() => {
        if (!cancelled) setStatus({ state: "offline" });
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return status;
}
