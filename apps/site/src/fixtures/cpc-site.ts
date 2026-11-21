/**
 * Points the working folder at the fixed cpc site when a test file imports this module, so code that runs at import reads it.
 * The readers of public/ read the working folder on each call, so a test file still sets the folder in `beforeEach`.
 */
import { readFixtureSite } from "@/fixtures/sites";

readFixtureSite("cpc");
