/**
 * The menu href of the waiver package: the waiver page of the latest week with a waiver file.
 * The registry of the client build imports it only when the client takes waiver.
 */
import { currentWaiverHref } from "@/lib/data/waiver-data";

export const menuHref = (): string | null => currentWaiverHref();
