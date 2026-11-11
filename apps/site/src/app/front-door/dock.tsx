/**
 * The dock of the front door that holds the chips and the ask box. A dock that leaves in the cross-fade of reduced
 * motion hides from a screen reader and takes no input, so the page holds one ask box.
 */
"use client";

import { motion, useIsPresent } from "framer-motion";
import type { ComponentProps } from "react";

export function Dock(props: ComponentProps<typeof motion.div>) {
  const present = useIsPresent();
  return <motion.div {...props} aria-hidden={present ? undefined : true} inert={!present || undefined} />;
}
