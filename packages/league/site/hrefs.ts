/**
 * The href builders of a manager page that need no base path: each one takes the managers index href that a part holds.
 * The week and the managers both link a manager page, so the league package holds them. The app joins the base path in
 * src/lib/routes.ts and passes the index href down, so a part keeps no path format of its own.
 */

/* A component holds only the managers index href, so it calls this for a manager page and keeps no path format of its own. */
export const managerHrefFrom = (managersHref: string, rosterId: number) => `${managersHref}${rosterId}/`;
/* The manager page href of one team, or null when the season has no managers file, so a part renders the name as plain text.
   managerHref is taken by the season form in src/lib/routes.ts, so this one takes the managers index href that a component holds. */
export const managerHrefOrNull = (managersHref: string | null, rosterId: number) =>
  managersHref === null ? null : managerHrefFrom(managersHref, rosterId);
