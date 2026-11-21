/**
 * A lint fixture: a file in the fixture copy of the ui folder that imports the ui-sdk scope.
 * The design rule test expects the lint to pass it, because the ui folder holds the wrappers.
 */
import { Drawer } from "@ui-sdk/react";

export const Sheet = Drawer;
