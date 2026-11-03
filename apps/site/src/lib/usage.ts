/**
 * Usage counting helpers for GoatCounter: the count URL and the event call.
 * The event call never throws, so a blocked or missing script cannot break the page.
 */
declare global {
  interface Window {
    goatcounter?: {
      count?: (vars: { path: string; title?: string; event?: boolean }) => void;
    };
  }
}

// An empty code means counting is off, so the layout renders no tag.
export function usageScriptUrl(code: string): string | null {
  return code ? `https://${code}.goatcounter.com/count` : null;
}

// Ad blockers remove the count script, so the call checks for it each time.
export function countEvent(name: string): void {
  if (typeof window === "undefined") return;
  try {
    window.goatcounter?.count?.({ path: name, event: true });
  } catch {
    // Counting must never break the page.
  }
}
