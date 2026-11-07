/**
 * The one port of the eggs routes for the egg button, the egg banner, the egg board, and the hunt, with the API of the build.
 * Board calls at one time share one request, so a page with the button, the banner, and the hunt reads the board once.
 */
import { eggsApi, type Board, type EggsApi } from "@cpc/eggs/lib/api";
import { eggsTarget } from "@/lib/config";

const base = eggsApi(eggsTarget);

// The board route shares the limit of 10 calls per minute of the other routes. The button, the banner, and the hunt
// mount at once on the home page, so they share the call in flight. A call after it settles reads the board fresh.
let inFlight: Promise<Board> | null = null;

export const boardApi: EggsApi = {
  ...base,
  board: () => {
    inFlight ??= base.board().finally(() => {
      inFlight = null;
    });
    return inFlight;
  },
};
