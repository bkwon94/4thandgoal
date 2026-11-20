/**
 * Points the working folder at the fixed cpc site when a test file imports this module, before any reader of public/ loads.
 * A reader takes its folder when it loads, and the imports of a file run in order, so a test file lists this import first.
 */
import { readFixtureSite } from "@/fixtures/sites";

readFixtureSite("cpc");
