/**
 * The card: a plain surface of the page with a 20px radius and 16px of inner space.
 * The brand edge marks an open card, such as a game card with its recap open.
 */
import type { ReactNode } from "react";
import { cn } from "../lib/utils";

type CardProps = {
  children: ReactNode;
  // The element of the card. A card in a list is an li, and a card that stands alone is an article or a div.
  as?: "div" | "article" | "li" | "section";
  // True gives the card the brand edge.
  edge?: boolean;
  className?: string;
};

export function Card({ children, as: Element = "div", edge = false, className }: CardProps) {
  return (
    <Element
      className={cn("rounded-card border bg-card p-sp-4 text-ink", edge ? "border-accent" : "border-rule", className)}
    >
      {children}
    </Element>
  );
}
