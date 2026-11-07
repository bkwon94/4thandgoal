/**
 * The menu link of the sim package: none, because the sim has no page of its own and adds no menu item (PRD).
 * The registry of the client build imports it only when the client takes sim.
 */
import type { Destination } from "@cpc/design/shell/nav";

export const menuLink = (): Destination | null => null;
