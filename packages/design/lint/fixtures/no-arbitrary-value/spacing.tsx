/**
 * A lint fixture: an arbitrary spacing value in a cn(...) call.
 * The value rule test expects design/no-arbitrary-value to fail it at line 9.
 */
import { cn } from "@/lib/utils";

export const Rail = ({ open }: { open: boolean }) => (
  <nav
    className={cn("sticky", "top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)]", open && "opacity-100")}
  />
);
