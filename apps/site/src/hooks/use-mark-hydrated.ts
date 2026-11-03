/**
 * The hook that marks the root once the client script runs.
 * The mark hands every reveal from the CSS safety rule to Framer Motion.
 */
import { useEffect } from "react";

/* Sets data-hydrated on the root once the script runs. The attribute turns off the CSS safety rule in globals.css,
   so Framer Motion owns every reveal after hydration. The set is the same each time, so the first caller is enough. */
export function useMarkHydrated() {
  useEffect(() => {
    document.documentElement.setAttribute("data-hydrated", "");
  }, []);
}
