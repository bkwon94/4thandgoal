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

/* The failures that a test can give the fake: an error for each check, or an error for each claim, such as a 409. */
export type FakeFailures = { check?: EggsError; claim?: EggsError };

/* A copy of the board fixture where each roster holds the letters given for each egg word, such as
   { EAGLES: { 3: ["E", "A", "G", "L", "E"] } }. A test builds the state it needs from the real fixture. */
export function boardWith(held: Record<string, Record<number, string[]>>): Board {
  return {
    ...board,
    words: board.words.map((word) => ({
      ...word,
      managers: word.managers.map((manager) => ({ ...manager, letters: held[word.word]?.[manager.roster_id] ?? [] })),
    })),
  };
}

/* True when the letters fill the egg word: each letter of the word, as many times as the word holds it. */
function fills(letters: string[], word: string): boolean {
  return [...letters].sort().join("") === [...word].sort().join("");
}

/* The fake answers each check with `answer`, and each claim with the letter of the check in the egg word.
   The claim answer adds the letter to the letters of the roster on `state`, and names the winner when they fill the word. */
export function fakeEggsApi(answer: CheckAnswer, failures: FakeFailures = {}, state: Board = board): FakeEggsApi {
  const checks: EggCheck[] = [];
  const claims: EggClaim[] = [];
  return {
    checks,
    claims,
    check: async (check) => {
      checks.push(check);
      if (failures.check) throw failures.check;
      return answer;
    },
    claim: async (passphrase, claim): Promise<ClaimAnswer> => {
      if (passphrase !== PASSPHRASE) throw new EggsError(401, "Unauthorized");
      if (failures.claim) throw failures.claim;
      claims.push(claim);
      const letter = answer.match ? answer.letter : "";
      const letters = Object.fromEntries(
        state.words.map((word) => {
          const held = word.managers.find((manager) => manager.roster_id === claim.roster_id)?.letters ?? [];
          return [word.word, word.word === claim.word ? [...held, letter] : held];
        }),
      );
      const won = claim.word !== null && fills(letters[claim.word], claim.word);
      return {
        egg_id: 1,
        letter,
        roster_id: claim.roster_id,
        word: claim.word,
        letters,
        winner: won && claim.word !== null ? { roster_id: claim.roster_id, word: claim.word } : null,
      };
    },
    board: async () => state,
  };
}
