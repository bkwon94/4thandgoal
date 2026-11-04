/**
 * The menu href of the analyzer package: the Trade Analyzer page.
 * The registry of the client build imports it only when the client takes analyzer.
 */
import { analyzeHref } from "@/lib/routes";

export const menuHref = (): string | null => analyzeHref();
