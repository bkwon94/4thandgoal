/**
 * The aria-current value of a menu link.
 * It lives apart from the menu, so the server component of the masthead can call it.
 */
import type { Destination } from "./menu";

/* "page" for the link to the open page, else none. One place sets it for every link. */
export function currentPage(destination: Destination, pageHref?: string) {
  return destination.href === pageHref ? "page" : undefined;
}
