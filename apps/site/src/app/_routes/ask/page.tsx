/**
 * The hidden route /ask/ of the front door. The client build writes its route only while the flag front_door is off, so
 * the commissioner tests the front door on the live site. No link reaches it, and noindex keeps it out of search.
 */
import type { Metadata } from "next";
import { pageTitle } from "@/app/shell-props";
import FrontDoorPage from "@/app/front-door/door-page";

/* The path of the route. It matches no menu item, so no item of the menu shows as current. */
const ASK_HREF = "/ask/";

export const metadata: Metadata = {
  title: pageTitle(),
  robots: { index: false },
};

export default function AskPage() {
  return <FrontDoorPage pageHref={ASK_HREF} />;
}
