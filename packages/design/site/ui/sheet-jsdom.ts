/**
 * The jsdom stand-ins that a test needs before it opens the sheet. A test imports this file for its side effects.
 * Each stand-in is inert and fills a browser API that jsdom lacks. The Drawer itself runs for real.
 */

/* The Drawer measures its sheet with a ResizeObserver. This one feeds the Drawer no size. */
if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

/* The Drawer asks for the running animations when it closes, and an empty list lets it finish. */
if (typeof Element.prototype.getAnimations !== "function") {
  Element.prototype.getAnimations = () => [];
}

/* The menu sheet listens for the desktop tier while it is open, so it closes there. This one matches no query, as a
   phone does, and it never fires a change. */
if (typeof window.matchMedia !== "function") {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList;
}

/* A browser has the popover API, and the Drawer puts its dim and its sheet in the top layer with it. With no popover API,
   the Drawer gives them a high inline z-index instead. These let jsdom take the browser path. The menu sheet passes the body
   as its container, so a browser and jsdom both render its dim and its sheet in the body. These do not change that place. */
if (typeof HTMLElement.prototype.showPopover !== "function") {
  Object.defineProperty(HTMLElement.prototype, "popover", {
    configurable: true,
    get(this: HTMLElement) {
      return this.getAttribute("popover");
    },
    set(this: HTMLElement, value: string) {
      this.setAttribute("popover", value);
    },
  });
  HTMLElement.prototype.showPopover = function () {};
  HTMLElement.prototype.hidePopover = function () {};
  HTMLElement.prototype.togglePopover = () => true;
}
