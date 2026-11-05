/**
 * The count script tag of the head. The root layout renders it with usage_code from the client values.
 * A client with no usage_code gets no tag, so its site loads no count script.
 */
import { usageScriptUrl } from "../lib/usage";

export function UsageScript({ code }: { code: string | null }) {
  const url = usageScriptUrl(code);
  // The count script skips localhost on its own, so dev builds send nothing.
  return url ? <script async data-goatcounter={url} src="https://gc.zgo.at/count.js" /> : null;
}
