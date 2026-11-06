/**
 * The menu link of the midseason package: none, because the report adds no menu item and no dock item (PRD).
 * The registry of the client build imports it only when the client takes midseason.
 */
import type { Destination } from "@cpc/design/shell/nav";

export const menuLink = (): Destination | null => null;
