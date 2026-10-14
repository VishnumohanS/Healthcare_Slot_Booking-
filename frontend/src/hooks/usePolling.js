import { useEffect, useRef } from "react";

/** Calls `callback` every `intervalMs` while the tab is visible (optional real-time refresh). */
export default function usePolling(callback, intervalMs) {
  const saved = useRef(callback);
  useEffect(() => {
    saved.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!intervalMs) return undefined;
    const id = setInterval(() => {
      if (document.visibilityState === "visible") saved.current();
    }, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
}
