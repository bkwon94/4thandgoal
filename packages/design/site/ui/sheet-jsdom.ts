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

/* With no popover API, the Drawer moves its dim and its sheet to the end of the body. A browser has one, and there the
   Drawer renders them in place, inside the band. These give jsdom the browser placement, so a test sees what a browser does. */
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
