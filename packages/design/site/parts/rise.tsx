/**
 * The rise of the look: content fades and rises in once on load, in a stagger, 0.7s on the curve of the look.
 * Reduced motion and a page with no script show the content at rest, through the reveal it wraps.
 */
import type { ReactNode } from "react";
import { DURATION, RISE_EASE, stagger } from "../lib/motion";
import { Reveal } from "./reveal";

type RiseProps = {
  children: ReactNode;
  // The place of the box in the stagger of the page: 0 rises first.
  step?: number;
  className?: string;
};

export function Rise({ children, step = 0, className }: RiseProps) {
  return (
    <Reveal trigger="mount" delay={stagger(step)} duration={DURATION.rise} ease={RISE_EASE} className={className}>
      {children}
    </Reveal>
  );
}
