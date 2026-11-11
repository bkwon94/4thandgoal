/**
 * The home page at /. The flag front_door of client.toml picks it: on, / is the front door; off, / is the Front page of
 * decision 08, and the front door sits at the hidden /ask/ route until the commissioner turns it on (ticket 43 of front-door).
 */
import type { Metadata } from "next";
import { clientValues } from "@/generated/client-values";
import { pageTitle } from "@/app/shell-props";
import FrontDoorPage from "@/app/front-door/door-page";
import FrontPage from "@/app/front-page";

export const metadata: Metadata = {
  title: pageTitle(),
};

export default function HomePage() {
  return clientValues.frontDoor ? <FrontDoorPage /> : <FrontPage />;
}
