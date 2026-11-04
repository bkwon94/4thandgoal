/**
 * The menu href of the managers package: the managers index of the latest season.
 * The registry of the client build imports it only when the client takes managers.
 */
import { currentManagersHref } from "@/lib/data/manager-data";

export const menuHref = (): string | null => currentManagersHref();
