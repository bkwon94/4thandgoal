/**
 * The pick of the stored run that the replay of the sim page plays. Each stored run of a What-if follows the set results,
 * and its weight says how likely it is, so the pick takes a run with a chance in proportion to its weight.
 */

/* `random` gives a number in [0, 1), as Math.random does. The line from 0 to 1 holds one piece per run, as long as
   its share of the weights, and the run whose piece holds the number comes up. A run of weight 0 has no piece. */
export function pickRun(weights: number[], random: () => number): number {
  const total = weights.reduce((sum, weight) => sum + weight, 0);
  const at = random() * total;
  let end = 0;
  let last = 0;
  for (const [index, weight] of weights.entries()) {
    if (weight <= 0) continue;
    end += weight;
    last = index;
    if (at < end) return index;
  }
  // The sum of floats can end a hair under `at`, so the last run with a weight takes the rest of the line.
  return last;
}
