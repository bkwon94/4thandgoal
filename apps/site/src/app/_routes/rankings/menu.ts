/**
 * The menu href of the rankings package: the power rankings page.
 * The registry of the client build imports it only when the client takes rankings.
 */
import { rankingsHref } from "@/lib/routes";

export const menuHref = (): string | null => rankingsHref();
