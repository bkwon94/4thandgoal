/**
 * The preload of `bun test`. It gives each test file the happy-dom globals, as the Bun DOM docs show.
 * After each test, it unmounts each React Testing Library render and restores each spy and each stub of `./stubs`.
 */
import { GlobalRegistrator } from "@happy-dom/global-registrator";
import { afterEach, mock } from "bun:test";

GlobalRegistrator.register();

// A canceled animation rejects its `finished` promise. A browser marks that promise as handled, as the Web Animations
// spec says, so a page that never reads it sees no error. happy-dom does not, so each Framer Motion animation that a test
// unmounts fails the run with an unhandled AbortError. `cancel` is the one place that rejects the promise, so this wrap
// marks the promise as handled first. A caller that reads the promise still sees the rejection.
const cancel = Animation.prototype.cancel;
Animation.prototype.cancel = function (this: Animation) {
  this.finished.catch(() => {});
  cancel.call(this);
};

// Import these after the register, because React Testing Library reads `document` when it loads.
const { cleanup } = await import("@testing-library/react");
const { restoreStubs } = await import("./stubs");

afterEach(() => {
  cleanup();
  // Each `spyOn` and each stub lasts for one test, so no test file leaks a fake into the next file of the same run.
  mock.restore();
  restoreStubs();
});
