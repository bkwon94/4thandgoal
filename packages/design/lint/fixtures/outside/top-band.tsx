/**
 * A lint fixture: a file outside the ui folder that imports the ui-sdk scope.
 * The design rule test expects no-restricted-imports to fail it at line 5.
 */
import { Drawer } from "@ui-sdk/react";

export const Part = Drawer;
