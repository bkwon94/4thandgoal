/**
 * The one fake of the eggs port for the site tests, over the board fixture that the API tests hold to the real answer.
 * The fake keeps each check and each claim it gets, so a test reads what the parts sent.
 */
import boardJson from "./board.json";
import {
  boardSchema,
  EggsError,
  type Board,
  type CheckAnswer,
  type ClaimAnswer,
  type EggCheck,
  type EggClaim,
  type EggsApi,
} from "../api";

/* The parse runs at import, so a stale fixture fails at once. */
export const board: Board = boardSchema.parse(boardJson);

/* The passphrase that the fake takes. Any other passphrase is a 401, as the API answers. */
export const PASSPHRASE = "localtest";

export type FakeEggsApi = EggsApi & { checks: EggCheck[]; claims: EggClaim[] };

/* The fake answers each check with `answer`, and each claim with the letter of the check in the egg word. */
export function fakeEggsApi(answer: CheckAnswer): FakeEggsApi {
  const checks: EggCheck[] = [];
  const claims: EggClaim[] = [];
  return {
    checks,
    claims,
    check: async (check) => {
      checks.push(check);
      return answer;
    },
    claim: async (passphrase, claim): Promise<ClaimAnswer> => {
      if (passphrase !== PASSPHRASE) throw new EggsError(401, "Unauthorized");
      claims.push(claim);
      const letter = answer.match ? answer.letter : "";
      const letters = Object.fromEntries(board.words.map((word) => [word.word, word.word === claim.word ? [letter] : []]));
      return { egg_id: 1, letter, roster_id: claim.roster_id, word: claim.word, letters };
    },
    board: async () => board,
  };
}
