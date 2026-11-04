/**
 * The menu of the site: the menu button and the sheet it opens, the desktop row with the Past weeks popover, and the compact bar.
 * It is the client island of the masthead, so the masthead stays a server component and passes the destinations in.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useId, useRef, useState, type ReactNode, type Ref } from "react";
import { currentPage } from "@/components/shell/current-page";
import { Dialog, DialogOverlay, DialogPopup, DialogPortal, DialogTrigger } from "@/components/ui/dialog";
import { ThemeButton } from "@/components/shell/theme-button";
import { Popover, PopoverClose, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useMotionOff } from "@/hooks/use-motion-off";
import { DROP, DURATION, EASE_OUT, INSTANT, stagger } from "@/lib/motion";

/* One place the menu links to. The href carries the base path, because every link is a plain anchor. */
export type Destination = { label: string; href: string };

/* The home link and the logo src of the brand, each with the base path. The logo src sits with the link, because it takes the base path the same way. */
export type Brand = { home: string; logo: string };

/* The destinations of the menu: the pages first, then the past weeks, newest first, under their own heading. */
export type Destinations = { pages: Destination[]; pastWeeks: Destination[] };

type MenuProps = {
  destinations: Destinations;
  // The href of the open page. The item with the same href carries the current-page state.
  pageHref?: string;
};

type MenuIslandProps = MenuProps & {
  // The brand title of the masthead. It names the home link of the compact bar, where the logo shows with no title.
  title: string;
  // The home link and the logo of the compact bar. The masthead passes its own.
  brand: Brand;
};

/* The distance in px of the top and the bottom line of the icon from its middle line. */
const LINE_GAP = 5;

/* The menu button icon: three lines that turn into a cross. With motion off, the icon switches with no morph. */
function MenuIcon({ open, off }: { open: boolean; off: boolean }) {
  const transition = off ? INSTANT : { duration: DURATION.iconMorph, ease: EASE_OUT };
  const line = "absolute inset-x-0 top-1/2 -mt-px h-sp-0 rounded-full bg-current";
  return (
    <span aria-hidden className="relative block size-sp-5">
      <motion.span
        className={line}
        initial={false}
        animate={open ? { y: 0, rotate: 45 } : { y: -LINE_GAP, rotate: 0 }}
        transition={transition}
      />
      <motion.span className={line} initial={false} animate={{ opacity: open ? 0 : 1 }} transition={transition} />
      <motion.span
        className={line}
        initial={false}
        animate={open ? { y: 0, rotate: -45 } : { y: LINE_GAP, rotate: 0 }}
        transition={transition}
      />
    </span>
  );
}

type MenuButtonProps = { open: boolean; off: boolean; listId: string; className: string; ref?: Ref<HTMLButtonElement> };

/* The menu button, shared by the masthead and the compact bar, so both keep the same name, state, and look. */
function MenuButton({ open, off, listId, className, ref }: MenuButtonProps) {
  return (
    <DialogTrigger
      ref={ref}
      aria-label="Menu"
      // The list lives in a portal that exists only while the sheet is open, so the reference exists only then.
      aria-controls={open ? listId : undefined}
      className={`press -mr-sp-3 flex size-touch flex-none items-center justify-center text-on-dark hover-fine:text-accent-text ${className}`}
    >
      <MenuIcon open={open} off={off} />
    </DialogTrigger>
  );
}

type ItemProps = { destination: Destination; pageHref?: string; index: number; off: boolean };

/* One link of the menu. A plain anchor, so the static export navigates with scripts off and with no client router. */
function Item({ destination, pageHref, index, off }: ItemProps) {
  return (
    <motion.li
      initial={off ? false : { opacity: 0, y: DROP }}
      animate={{ opacity: 1, y: 0 }}
      transition={off ? INSTANT : { duration: DURATION.collapse, ease: EASE_OUT, delay: stagger(index) }}
    >
      {/* The current-page state sets the red accent too, so the mark a reader sees and the state a screen reader speaks never differ. */}
      <a
        href={destination.href}
        aria-current={currentPage(destination, pageHref)}
        className="press flex min-h-touch items-center border-b border-rule text-lead font-bold text-ink no-underline hover-fine:text-accent-ink aria-[current=page]:text-accent-ink"
      >
        {destination.label}
      </a>
    </motion.li>
  );
}

/* One link of the desktop row. The band is black, so the red accent is the light red, as in the noscript row of the masthead.
   A label never wraps, so the brand title wraps first when the line is short. */
function RowLink({ destination, pageHref }: { destination: Destination; pageHref?: string }) {
  return (
    <a
      href={destination.href}
      aria-current={currentPage(destination, pageHref)}
      className="press inline-flex min-h-touch items-center text-label font-bold tracking-caps whitespace-nowrap text-on-dark uppercase no-underline hover-fine:text-accent-text aria-[current=page]:text-accent-text"
    >
      {destination.label}
    </a>
  );
}

/* The scale the popover starts from. It is close to 1, so the popover grows out of its trigger and does not pop. */
const POPOVER_SCALE = 0.95;

type RowProps = MenuProps & {
  // The name of the landmark. The compact bar holds a second row, so each row takes its own name and a screen reader tells them apart.
  label: string;
  // The placement of the row in its parent.
  className: string;
  // True for the row of the compact bar, which ends with the theme button. The masthead shows its theme button on the brand line.
  withThemeButton: boolean;
};

/* The menu as a row of links for the desktop tier. It renders the same destinations as the sheet, so an item lives in one place. */
function Row({ destinations, pageHref, label, className, withThemeButton }: RowProps) {
  const off = useMotionOff();
  const [pastOpen, setPastOpen] = useState(false);
  // The popover leaves faster than it enters, along the same path. With motion off it leaves at once.
  const popoverExit = off
    ? { opacity: 0, transition: INSTANT }
    : { opacity: 0, scale: POPOVER_SCALE, transition: { duration: DURATION.popoverExit, ease: EASE_OUT } };
  return (
    // The row shows from the desktop tier up, where the menu button hides. With scripts off the noscript row of the masthead takes its place.
    <nav
      aria-label={label}
      className={`hidden items-center gap-x-sp-4 desktop:flex [@media(scripting:none)]:hidden ${className}`}
    >
      {destinations.pages.map((destination) => (
        <RowLink key={destination.href} destination={destination} pageHref={pageHref} />
      ))}
      {destinations.pastWeeks.length > 0 && (
        // Focus stays inside the open popover, as it does in the sheet. The page still scrolls and takes a click outside.
        <Popover open={pastOpen} onOpenChange={setPastOpen} modal="trap-focus">
          <PopoverTrigger className="press inline-flex min-h-touch items-center text-label font-bold tracking-caps whitespace-nowrap text-on-dark uppercase hover-fine:text-accent-text">
            Past Weeks
          </PopoverTrigger>
          {/* Framer Motion owns the scale and the fade, so the CSS keyframes and the CSS transition of the primitive are off.
              The duration-100 of the primitive gives a transition on every property. Framer writes the end opacity and scale
              when its animation ends, and WebKit then runs them from the start values again, so the popover blinks.
              The primitive sets transform-origin to Base UI's --transform-origin, so the popover grows from the trigger.
              Base UI keeps the portal while the exit plays, and AnimatePresence removes it after, as the sheet does. */}
          <AnimatePresence>
            {pastOpen && (
              <PopoverContent
                keepMounted
                aria-label="Past Weeks"
                align="end"
                className="w-48 gap-0 rounded-none p-0 px-sp-4 py-sp-1 transition-none data-open:animate-none data-closed:animate-none"
                render={
                  <motion.div
                    initial={off ? false : { opacity: 0, scale: POPOVER_SCALE }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={popoverExit}
                    transition={off ? INSTANT : { duration: DURATION.popover, ease: EASE_OUT }}
                  />
                }
              >
                <ul className="m-0 list-none p-0">
                  {destinations.pastWeeks.map((destination) => (
                    <li key={destination.href} className="border-b border-rule last:border-b-0">
                      <a
                        href={destination.href}
                        aria-current={currentPage(destination, pageHref)}
                        className="press flex min-h-touch items-center text-lead font-bold text-ink no-underline hover-fine:text-accent-ink aria-[current=page]:text-accent-ink"
                      >
                        {destination.label}
                      </a>
                    </li>
                  ))}
                </ul>
                {/* Base UI asks for a close control in a popover that traps focus, so a touch screen reader can leave it.
                    A keyboard closes the popover with Escape, so Tab skips the control, and it shows to no one. */}
                <PopoverClose tabIndex={-1} className="sr-only">
                  Close Past Weeks
                </PopoverClose>
              </PopoverContent>
            )}
          </AnimatePresence>
        </Popover>
      )}
      {/* The row of the compact bar ends with the theme button, where the menu button sits below the desktop tier.
          The negative margin lines the icon up with the page edge, as the menu button does. */}
      {withThemeButton && <ThemeButton className="-mr-sp-3" />}
    </nav>
  );
}

type CompactBarProps = {
  title: string;
  brand: Brand;
  off: boolean;
  children: ReactNode;
  ref: Ref<HTMLDivElement>;
};

/* The compact bar: a 44px black bar fixed to the top of the viewport, with the brand mark and the menu.
   It is fixed, so it takes no space in the page flow and the page under it never jumps. */
function CompactBar({ title, brand, off, children, ref }: CompactBarProps) {
  // The bar slides down from above the viewport and fades in, and leaves along the same path. With motion off it only cross-fades.
  const offset = off ? {} : { y: "-100%" };
  return (
    <motion.div
      ref={ref}
      role="region"
      // A reader does not know the word "compact bar", so the landmark takes a name for where the bar sits.
      aria-label="Top bar"
      className="fixed inset-x-0 top-0 z-40 h-touch bg-band text-on-dark"
      initial={{ opacity: 0, ...offset }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, ...offset }}
      transition={{ duration: DURATION.bar, ease: EASE_OUT }}
    >
      {/* The same box as the masthead, so the content of the bar lines up with the page column. */}
      <div className="mx-auto flex h-full max-w-page items-center justify-between gap-sp-3 px-gutter">
        {/* The bar shows the logo with no title, so the logo names the home link. */}
        {/* The link takes the full height of the bar, so it is a 44px tap target around the 30px logo. */}
        <a href={brand.home} className="flex h-touch flex-none items-center">
          <img src={brand.logo} alt={title} width={30} height={30} className="size-logo rounded-full" />
        </a>
        {children}
      </div>
    </motion.div>
  );
}

export function Menu({ destinations, pageHref, title, brand }: MenuIslandProps) {
  const [open, setOpen] = useState(false);
  const off = useMotionOff();
  const listId = useId();
  const pastId = useId();
  const buttonRef = useRef<HTMLButtonElement>(null);
  const barRef = useRef<HTMLDivElement>(null);
  // The top of the sheet in the viewport. The sheet hangs from the bottom of the compact bar while the bar shows,
  // else from the bottom of the masthead, or from the top once the masthead scrolls out.
  const [top, setTop] = useState(0);
  // True while the masthead is out of the viewport. The compact bar shows then. With scripts off it stays false, so the bar never renders.
  const [barShown, setBarShown] = useState(false);

  // The menu button lives in the masthead, so its header is the masthead. The observer watches it and the bar follows it.
  useEffect(() => {
    const masthead = buttonRef.current?.closest("header");
    if (!masthead || typeof IntersectionObserver === "undefined") return;
    const observer = new IntersectionObserver(([entry]) => setBarShown(!entry.isIntersecting));
    observer.observe(masthead);
    return () => observer.disconnect();
  }, []);

  function openChange(next: boolean) {
    if (next) {
      const anchor = barShown ? barRef.current : buttonRef.current?.closest("header");
      setTop(Math.max(0, anchor?.getBoundingClientRect().bottom ?? 0));
    }
    setOpen(next);
  }

  // The sheet drops and fades in, and leaves faster along the same path. With motion off it only cross-fades.
  const offset = off ? {} : { y: DROP };
  const sheet = {
    initial: { opacity: 0, ...offset },
    animate: { opacity: 1, y: 0, transition: { duration: DURATION.collapse, ease: EASE_OUT } },
    exit: { opacity: 0, ...offset, transition: { duration: DURATION.sheetExit, ease: EASE_OUT } },
  };
  const backdrop = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: DURATION.collapse, ease: EASE_OUT } },
    exit: { opacity: 0, transition: { duration: DURATION.sheetExit, ease: EASE_OUT } },
  };
  // The index of an item in the whole sheet, so the past weeks continue the stagger of the pages.
  const pastStart = destinations.pages.length;

  return (
    <>
      {/* From the desktop tier the masthead row takes its own line under the brand line, across the full column.
          The desktop type step made the links wider than the column holds beside a two-line brand title,
          so on one line the title wrapped to one word per line. The brand row is a grid at the desktop tier, and this is its second row. */}
      <Row
        destinations={destinations}
        pageHref={pageHref}
        label="Site menu"
        className="desktop:col-span-2 desktop:row-start-2"
        withThemeButton={false}
      />
      <Dialog open={open} onOpenChange={openChange}>
        {/* With scripts off the button can open nothing, so it hides, and the masthead shows the destinations as plain links.
            From the desktop tier up the row shows the destinations, so the button hides. */}
        {/* The theme button sits left of the menu button. The auto margin takes the free space of the row,
            so the two buttons stay together at the right end and the brand link stays at the left.
            From the desktop tier the menu button hides, and the theme button stays at the right end of the brand line, in the second cell of the grid.
            The negative margin there lines the icon up with the page edge, as the menu button does below the desktop tier. */}
        <ThemeButton className="ml-auto desktop:col-start-2 desktop:row-start-1 desktop:-mr-sp-3 [@media(scripting:none)]:hidden" />
        <MenuButton
          ref={buttonRef}
          open={open}
          off={off}
          listId={listId}
          className="desktop:hidden [@media(scripting:none)]:hidden"
        />
        <AnimatePresence>
          {barShown && (
            <CompactBar ref={barRef} title={title} brand={brand} off={off}>
              <Row destinations={destinations} pageHref={pageHref} label="Top bar menu" className="" withThemeButton />
              {/* The bar never renders with scripts off, so the theme button here needs no scripting rule. */}
              <ThemeButton className="ml-auto desktop:hidden" />
              {/* A second trigger of the same dialog. Base UI marks the trigger that opened the sheet, so focus returns to it on close. */}
              <MenuButton open={open} off={off} listId={listId} className="desktop:hidden" />
            </CompactBar>
          )}
        </AnimatePresence>
        {/* Base UI keeps the portal while the exit plays, and AnimatePresence removes it after, as the Base UI docs show for Motion. */}
        <AnimatePresence>
          {open && (
            <DialogPortal keepMounted>
              {/* The dimmed page starts under the masthead or the compact bar, so the bar and the cross of the button stay clear.
                  Framer Motion owns the fade, so the CSS fade, the CSS transition, and the blur of the primitive are off.
                  The duration-100 of the primitive gives a transition on every property. Framer writes the end opacity
                  when its fade ends, and WebKit then fades the overlay from 0 again, so the dimmed page blinks. */}
              <DialogOverlay
                className="transition-none bg-band/50 data-open:animate-none data-closed:animate-none supports-backdrop-filter:backdrop-blur-none"
                style={{ top }}
                render={<motion.div {...backdrop} />}
              />
              {/* The bottom rule marks the end of the sheet. In the dark theme the sheet and the dimmed page are both black, so the edge is lost without it. */}
              <DialogPopup
                aria-label="Menu"
                className="fixed inset-x-0 z-50 overflow-y-auto overscroll-contain border-b border-rule bg-page text-ink outline-none"
                style={{ top, maxHeight: `calc(100dvh - ${top}px)` }}
                render={<motion.div {...sheet} />}
              >
                <nav id={listId} aria-label="Site menu" className="mx-auto max-w-page px-gutter pb-sp-6">
                  <ul className="m-0 list-none p-0">
                    {destinations.pages.map((destination, index) => (
                      <Item key={destination.href} destination={destination} pageHref={pageHref} index={index} off={off} />
                    ))}
                  </ul>
                  {destinations.pastWeeks.length > 0 && (
                    <>
                      <h2
                        id={pastId}
                        className="mt-sp-5 mb-0 text-label leading-tight font-bold tracking-wide text-accent-ink uppercase"
                      >
                        Past Weeks
                      </h2>
                      <ul aria-labelledby={pastId} className="m-0 list-none p-0">
                        {destinations.pastWeeks.map((destination, index) => (
                          <Item
                            key={destination.href}
                            destination={destination}
                            pageHref={pageHref}
                            index={pastStart + index}
                            off={off}
                          />
                        ))}
                      </ul>
                    </>
                  )}
                </nav>
              </DialogPopup>
            </DialogPortal>
          )}
        </AnimatePresence>
      </Dialog>
    </>
  );
}
