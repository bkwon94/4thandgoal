/**
 * The spring sampler of the Open card: a damped spring, sampled into a CSS linear() curve.
 * The browser runs the curve as a plain transition, so a spring needs no script per frame (ADR 0028).
 */

/* The part of the start offset that may remain at the end of the curve. The last stop is set to 1, so a rest this small never shows. */
const REST = 0.001;

/*
 * A linear() curve of a damped spring from 0 to 1, over the full duration of the transition.
 * The bounce is from 0 to under 1: 0 settles with no overshoot, and a higher bounce overshoots more.
 * The default bounce of 0.3 overshoots by about 5%, the small overshoot of the Showcase Card method.
 */
export function springCurve({ bounce = 0.3, steps = 40 }: { bounce?: number; steps?: number } = {}): string {
  // The damping ratio: 1 is critical damping, and a lower ratio swings past the end.
  const damping = 1 - Math.min(Math.max(bounce, 0), 0.9);
  // The natural frequency that shrinks the swing to REST by the end of the duration.
  const frequency = Math.log(1 / REST) / damping;
  const position = (t: number) => {
    const decay = Math.exp(-damping * frequency * t);
    if (damping >= 1) return 1 - decay * (1 + frequency * t);
    const swing = frequency * Math.sqrt(1 - damping * damping);
    return 1 - decay * (Math.cos(swing * t) + ((damping * frequency) / swing) * Math.sin(swing * t));
  };
  const values = Array.from({ length: steps + 1 }, (_, step) => Math.round(position(step / steps) * 10000) / 10000);
  // The ends are exact, so the transition starts and stops at its two states.
  values[0] = 0;
  values[steps] = 1;
  return `linear(${values.join(", ")})`;
}
