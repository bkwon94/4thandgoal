/**
 * The jsdom stand-in that a test needs when a sheet moves under a drag, or springs back from a refused dismissal.
 * A test calls standInForAnimate and keeps the returned function to put jsdom back as it was. The stand-in is not global,
 * because Framer Motion drives its animations with Element.animate when it exists, so a test of a page with Framer Motion
 * installs it for the one test that needs it.
 */

/* The Drawer moves a sheet with one animation. This one finishes at once, so a drag settles or closes in a test with no
   wait for a frame. */
export function standInForAnimate(): () => void {
  const before = Object.getOwnPropertyDescriptor(Element.prototype, "animate");
  Element.prototype.animate = function () {
    const animation = {
      startTime: null as number | null,
      cancel() {},
      set onfinish(handler: (() => void) | null) {
        if (handler) setTimeout(handler, 0);
      },
    };
    return animation as unknown as Animation;
  };
  return () => {
    if (before) Object.defineProperty(Element.prototype, "animate", before);
    else delete (Element.prototype as { animate?: unknown }).animate;
  };
}
