/**
 * The preload of `bun test`. It gives each test file the happy-dom globals, as the Bun DOM docs show, with fixes where
 * happy-dom differs from a browser. After each test, it unmounts each render and restores each spy and each stub of `./stubs`.
 */
import { GlobalRegistrator } from "@happy-dom/global-registrator";
import { afterEach, mock } from "bun:test";

// A page always has a URL. With none, happy-dom resolves a relative `img` src to nothing and fires `error`, so an avatar
// shows its default image. The URL is the one of the dev server.
GlobalRegistrator.register({ url: "http://localhost:3000/" });

// happy-dom runs each animation frame as soon as it can, so a loop of `requestAnimationFrame` runs some hundred thousand
// frames each second and holds the CPU. A browser runs about 60. This queue runs the callbacks of each frame together,
// each with the same time, once each 1000 / 60 ms. A callback that a frame adds runs in the next frame, as in a browser.
const FRAME_MS = 1000 / 60;
// The frame timer uses the `setTimeout` of this moment. A test that replaces the global `setTimeout` with a fake clock
// must not hold the frame timer, because a fake clock that ends leaves a timer that never fires, and each later frame stalls.
const frameSetTimeout = globalThis.setTimeout;
let frameQueue = new Map<number, FrameRequestCallback>();
let lastFrameId = 0;
let frameTimer: ReturnType<typeof setTimeout> | null = null;
const runFrame = () => {
  frameTimer = null;
  const callbacks = frameQueue;
  frameQueue = new Map();
  const time = performance.now();
  for (const callback of callbacks.values()) {
    try {
      callback(time);
    } catch (error) {
      // A browser reports the error and runs the next callback. The throw in a microtask reports it to the run.
      queueMicrotask(() => {
        throw error;
      });
    }
  }
};
globalThis.requestAnimationFrame = (callback: FrameRequestCallback) => {
  lastFrameId += 1;
  frameQueue.set(lastFrameId, callback);
  frameTimer ??= frameSetTimeout(runFrame, FRAME_MS);
  return lastFrameId;
};
globalThis.cancelAnimationFrame = (id: number) => {
  frameQueue.delete(id);
};

// happy-dom binds each method of a storage to it on the first read, so a later `spyOn(Storage.prototype, ...)` has no
// effect. Each method here reads the prototype on each call, so a spy on the prototype acts, as in a browser. A define
// on the storage is the one way that its Proxy keeps a method and does not bind it.
for (const storage of [localStorage, sessionStorage]) {
  for (const name of ["getItem", "setItem", "removeItem", "clear", "key"] as const) {
    Object.defineProperty(storage, name, {
      configurable: true,
      writable: true,
      value: (...args: unknown[]) =>
        (Storage.prototype[name] as (...args: unknown[]) => unknown).apply(storage, args),
    });
  }
}

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
const { cleanup, prettyDOM } = await import("@testing-library/react");
const { restoreStubs } = await import("./stubs");

// Bun prints each own property of an object in a failed expect and in `console.log`. A happy-dom node reaches the whole
// window, so one failed `expect(node).toBeNull()` prints megabytes. In a `waitFor`, each failed check prints it again, and
// the run stalls for minutes. This prints a node as its markup, as Vitest does.
Object.defineProperty(Node.prototype, Bun.inspect.custom, {
  configurable: true,
  value(this: Node) {
    // prettyDOM takes an element or a document. Each other node prints its name and its text.
    const markup =
      this instanceof Element || this instanceof Document
        ? prettyDOM(this, 7000, { highlight: false })
        : false;
    return markup || `${this.nodeName} ${JSON.stringify(this.textContent?.slice(0, 200))}`;
  },
});

afterEach(() => {
  cleanup();
  // Each `spyOn` and each stub lasts for one test, so no test file leaks a fake into the next file of the same run.
  mock.restore();
  restoreStubs();
});
