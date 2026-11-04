/**
 * Tests for the War chest waiver page. They render the fixture with the week 6 teams and read what a reader sees.
 * jsdom applies no CSS and runs no animation, so the size and the drift tests read an inline style and a data attribute.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { renderToString } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { week6 } from "@cpc/week/fixtures/week-page";
import type { WaiverBoard, WaiverPlayer } from "@/lib/waiver-types";
import { waiver } from "@/fixtures/waiver";
import { WarChest } from "./war-chest";

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

function renderBoard(board: WaiverBoard = waiver) {
  render(<WarChest board={board} teams={week6.teams} avatars={{ "4": "/2026/week-06/avatars/4.jpg" }} />);
}

function rowsOf(name: string) {
  return within(screen.getByRole("list", { name })).getAllByRole("listitem");
}

function field() {
  return screen.getByRole("group", { name: "Top six" });
}

function sheet() {
  return screen.getByRole("region", { name: "Player sheet" });
}

describe("the budget ring", () => {
  it("shows twelve budgets in budget order, largest first", () => {
    renderBoard();
    const rows = rowsOf("Budgets");
    expect(rows.map((row) => row.textContent?.match(/\$(\d+)/)?.[1])).toEqual(
      ["90", "82", "72", "69", "67", "65", "61", "58", "51", "25", "19", "9"],
    );
  });

  it("names the team and shows its avatar, with no bar in red when no team is picked", () => {
    renderBoard();
    const first = rowsOf("Budgets")[0];
    expect(within(first).getByText("Pukancun on 3")).toBeTruthy();
    expect(first.querySelector("img")?.getAttribute("src")).toBe("/2026/week-06/avatars/4.jpg");
    for (const row of rowsOf("Budgets")) {
      expect(row.querySelector("[data-viewer]")).toBeNull();
    }
  });
});

describe("the bucket tabs", () => {
  it("shows one short tab per bucket in the file", () => {
    renderBoard();
    const tabs = within(screen.getByRole("group", { name: "Buckets" })).getAllByRole("button");
    expect(tabs.map((tab) => tab.textContent)).toEqual(["Best", "Trending", "Sneaky", "Stash", "Drops"]);
    expect(tabs[0].getAttribute("aria-pressed")).toBe("true");
  });

  it("switches the bucket, and the sheet keeps its player", () => {
    renderBoard();
    fireEvent.click(within(field()).getByRole("button", { name: /Courtland Sutton/ }));
    expect(within(sheet()).getByRole("heading", { name: "Courtland Sutton" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Stash" }));
    expect(screen.getByRole("button", { name: "Stash" }).getAttribute("aria-pressed")).toBe("true");
    expect(within(field()).getAllByRole("button").map((orb) => orb.getAttribute("aria-label"))).toEqual([
      "Mark Andrews, $8",
      "Audric Estime, $6",
    ]);
    // Courtland Sutton is not a stash, and the sheet still holds him.
    expect(within(sheet()).getByRole("heading", { name: "Courtland Sutton" })).toBeTruthy();
  });
});

describe("the drift field", () => {
  it("shows the top six of the bucket, sized by rank, each with its price", () => {
    renderBoard();
    const orbs = within(field()).getAllByRole("button");
    expect(orbs).toHaveLength(6);
    expect(orbs.map((orb) => orb.getAttribute("aria-label"))).toEqual([
      "Kenny Gainwell, $23",
      "Najee Harris, $14",
      "Mark Andrews, $8",
      "Audric Estime, $6",
      "Chris Godwin, $4",
      "Courtland Sutton, $3",
    ]);
    expect(within(orbs[0]).getByText("$23")).toBeTruthy();
    const sizes = orbs.map((orb) => orb.querySelector("img")!.style.width);
    expect(sizes).toEqual(["88px", "64px", "64px", "52px", "52px", "52px"]);
  });

  it("drifts with motion on, and stops when the document is hidden", () => {
    renderBoard();
    expect(field().getAttribute("data-drift")).toBe("on");
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "hidden" });
    act(() => {
      document.dispatchEvent(new Event("visibilitychange"));
    });
    expect(field().getAttribute("data-drift")).toBe("off");
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "visible" });
    act(() => {
      document.dispatchEvent(new Event("visibilitychange"));
    });
    expect(field().getAttribute("data-drift")).toBe("on");
  });
});

describe("the sheet", () => {
  it("opens on the top player of the best adds", () => {
    renderBoard();
    expect(within(sheet()).getByRole("heading", { name: "Kenny Gainwell" })).toBeTruthy();
    expect(within(sheet()).getByText("RB · TB · Bye 9")).toBeTruthy();
  });

  it("fills with the facts, the claims as links, the price, and the last like him on a tap of a headshot", () => {
    renderBoard();
    fireEvent.click(within(field()).getByRole("button", { name: "Najee Harris, $14" }));
    const open = within(sheet());
    expect(open.getByRole("heading", { name: "Najee Harris" })).toBeTruthy();
    const facts = within(open.getByRole("list", { name: "Facts" })).getAllByRole("listitem");
    expect(facts).toHaveLength(3);
    expect(facts[0].textContent).toBe("Najee Harris played 71% of snaps and took 6 targets last week, up from 48% and 3");
    const links = within(open.getByRole("list", { name: "Claims" })).getAllByRole("link");
    expect(links).toHaveLength(2);
    expect(links[0].textContent).toBe("Najee Harris took the lead role in practice this week.");
    expect(links[0].getAttribute("href")).toBe("https://sports.yahoo.com/fantasy/najee-harris-waiver");
    expect(open.getByText("Yahoo Fantasy · Backs the board")).toBeTruthy();
    expect(open.getByText("ESPN · Disputes the board")).toBeTruthy();
    expect(open.getByText("$14")).toBeTruthy();
    expect(open.getByText("$14 beats the top rival bid of $13")).toBeTruthy();
    // The last RB to win was Najee Harris himself, for $19 in week 4, by roster 3.
    expect(open.getByText("Last RB won")).toBeTruthy();
    expect(open.getByText("$19")).toBeTruthy();
    expect(open.getByText("Najee Harris, week 4, Lil Fridge")).toBeTruthy();
  });

  it("fills on a tap of a list row", () => {
    renderBoard();
    fireEvent.click(within(rowsOf("Also")[0]).getByRole("button"));
    expect(within(sheet()).getByRole("heading", { name: "Michael Mayer" })).toBeTruthy();
  });

  it("shows the trending count with a thousands separator", () => {
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Trending" }));
    fireEvent.click(within(field()).getByRole("button", { name: "Courtland Sutton, $3" }));
    expect(within(sheet()).getByText("31,877 adds on Sleeper in the last day")).toBeTruthy();
  });

  it("shows the injury status and the return week on the meta line", () => {
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Stash" }));
    fireEvent.click(within(field()).getByRole("button", { name: "Mark Andrews, $8" }));
    expect(within(sheet()).getByText("TE · BAL · Bye 7 · IR · Back week 9")).toBeTruthy();
  });

  it("labels a news claim as news", () => {
    renderBoard();
    fireEvent.click(within(field()).getByRole("button", { name: "Mark Andrews, $8" }));
    expect(within(sheet()).getByText("ESPN · News")).toBeTruthy();
  });

  it("names the sheet player in one short live line", () => {
    renderBoard();
    fireEvent.click(within(field()).getByRole("button", { name: "Najee Harris, $14" }));
    const live = sheet().querySelectorAll("[aria-live]");
    expect(live).toHaveLength(1);
    expect(live[0].textContent).toBe("Sheet: Najee Harris");
  });

  it("shows no last like him when no claim at the position won", () => {
    renderBoard();
    fireEvent.click(within(field()).getByRole("button", { name: "Chris Godwin, $4" }));
    expect(within(sheet()).queryByText(/^Last WR won/)).toBeNull();
  });

  it("says the experts are out only when the file flag is set", () => {
    renderBoard();
    expect(screen.queryByText("The experts are out this week.")).toBeNull();
    cleanup();
    renderBoard({ ...waiver, experts_missing: true });
    expect(within(sheet()).getByText("The experts are out this week.")).toBeTruthy();
  });
});

describe("the drops bucket", () => {
  it("names the roster that holds each drop on his headshot sheet, with the pool player who beats him", () => {
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Drops" }));
    // A drop has no price, so his headshot has no price tag and his name is the whole label.
    fireEvent.click(within(field()).getByRole("button", { name: "Austin Ekeler" }));
    const open = within(sheet());
    expect(open.getByText("On Lil Fridge")).toBeTruthy();
    expect(open.getByText("Kenny Gainwell projects 9.3 a week higher")).toBeTruthy();
    expect(open.queryByText("Bid to win")).toBeNull();
  });

  it("names the holder on a drops row after the top six", () => {
    // Seven drops, so the seventh goes in the list. Each copy gets its own id, so the keys stay unique.
    const ekeler = waiver.buckets.drops[0];
    const drops: WaiverPlayer[] = Array.from({ length: 7 }, (_, index) => ({ ...ekeler, player_id: `${ekeler.player_id}-${index}` }));
    renderBoard({ ...waiver, buckets: { ...waiver.buckets, drops } });
    fireEvent.click(screen.getByRole("button", { name: "Drops" }));
    const rows = rowsOf("Also");
    expect(rows).toHaveLength(1);
    expect(within(rows[0]).getByText("RB · WAS · Bye 12 · On Lil Fridge")).toBeTruthy();
  });
});

describe("the list", () => {
  it("holds the rest of the bucket from rank 7, with the price", () => {
    renderBoard();
    const rows = rowsOf("Also");
    expect(rows).toHaveLength(2);
    expect(rows[0].textContent).toBe("7Michael MayerTE · LV · Bye 8$2");
    expect(rows[1].textContent).toBe("8Austin EkelerRB · WAS · Bye 12$1");
  });

  it("is not there for a bucket of six or fewer", () => {
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Sneaky" }));
    expect(screen.queryByRole("list", { name: "Also" })).toBeNull();
  });
});

describe("the headshots", () => {
  it("shows the Sleeper headshot, and swaps a missing one to the default once", () => {
    renderBoard();
    const img = within(field()).getAllByRole("button")[0].querySelector("img")!;
    expect(img.getAttribute("src")).toBe("https://sleepercdn.com/content/nfl/players/7567.jpg");
    fireEvent.error(img);
    expect(img.getAttribute("src")).toBe("/images/headshot-default.svg");
    // A second error keeps the default, so a missing default file never loops.
    img.setAttribute("src", "broken.svg");
    fireEvent.error(img);
    expect(img.getAttribute("src")).toBe("broken.svg");
  });
});

/* The pick list, open when there is no pick. */
function pickList() {
  return screen.queryByRole("group", { name: "Your team" });
}

function chip() {
  return screen.queryByRole("region", { name: "Your team" });
}

describe("the team pick", () => {
  it("shows the team list open with no pick, and no chip", () => {
    renderBoard();
    expect(within(pickList()!).getAllByRole("radio")).toHaveLength(12);
    expect(chip()).toBeNull();
  });

  it("collapses the list to a chip with the team, the budget, and a Change link on a pick", () => {
    renderBoard();
    fireEvent.click(within(pickList()!).getByRole("radio", { name: /Pukancun on 3/ }));
    expect(pickList()).toBeNull();
    const picked = within(chip()!);
    expect(picked.getByText("Pukancun on 3")).toBeTruthy();
    expect(picked.getByText("you have $90")).toBeTruthy();
    expect(chip()!.querySelector("img")?.getAttribute("src")).toBe("/2026/week-06/avatars/4.jpg");
    expect(picked.getByRole("button", { name: "Change your team" })).toBeTruthy();
  });

  it("shows the default avatar on the chip for a team with no avatar, as the ring does", () => {
    localStorage.setItem("cpc.waiver-team", "3");
    renderBoard();
    const ring = within(rowsOf("Budgets")[2]);
    expect(ring.getByText("Lil Fridge")).toBeTruthy();
    expect(chip()!.querySelector("img")?.getAttribute("src")).toBe("/images/avatar-default.svg");
    expect(rowsOf("Budgets")[2].querySelector("img")?.getAttribute("src")).toBe("/images/avatar-default.svg");
  });

  it("holds an empty slot of the chip height until it reads storage", () => {
    const markup = renderToString(<WarChest board={waiver} teams={week6.teams} avatars={{}} />);
    expect(markup).toContain("h-pick-chip");
    expect(markup).not.toContain('name="Your team"');
  });
});

describe("the team pick across visits", () => {
  it("survives a reload through storage", () => {
    renderBoard();
    fireEvent.click(within(pickList()!).getByRole("radio", { name: /Lil Fridge/ }));
    cleanup();
    renderBoard();
    expect(pickList()).toBeNull();
    expect(within(chip()!).getByText("Lil Fridge")).toBeTruthy();
    expect(within(chip()!).getByText("you have $72")).toBeTruthy();
  });

  it("keeps the page working for the visit when storage throws", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    renderBoard();
    fireEvent.click(within(pickList()!).getByRole("radio", { name: /Lil Fridge/ }));
    expect(within(chip()!).getByText("you have $72")).toBeTruthy();
  });

  it("reads a roster id that the budget table does not hold as no pick", () => {
    localStorage.setItem("cpc.waiver-team", "99");
    renderBoard();
    expect(chip()).toBeNull();
    expect(within(pickList()!).queryByRole("radio", { checked: true })).toBeNull();
  });
});

describe("the ring and the sheet with a pick", () => {
  it("turns only the picked team's bar red", () => {
    localStorage.setItem("cpc.waiver-team", "3");
    renderBoard();
    const marked = rowsOf("Budgets").filter((row) => row.querySelector("[data-viewer]"));
    expect(marked).toHaveLength(1);
    expect(within(marked[0]).getByText("Lil Fridge")).toBeTruthy();
    expect(marked[0].querySelector("[data-viewer]")?.className).toContain("bg-accent");
  });

  it("names the bid as the line when the viewer's budget is above the bid", () => {
    localStorage.setItem("cpc.waiver-team", "3");
    renderBoard();
    const open = within(sheet());
    expect(open.getByText("Can outbid you")).toBeTruthy();
    // Lil Fridge has $72 and Kenny Gainwell's bid is $23. The outbid map holds 9 at "72".
    expect(open.getByText("9")).toBeTruthy();
    expect(open.getByText("Rivals over $23")).toBeTruthy();
  });

  it("names the budget as the line when the viewer's budget is below the bid, and follows a new pick", () => {
    localStorage.setItem("cpc.waiver-team", "3");
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Change your team" }));
    fireEvent.click(within(pickList()!).getByRole("radio", { name: /Maye d'force B with U/ }));
    // Maye d'force B with U has $19, below the $23 bid. The map holds 10 at "19".
    expect(within(chip()!).getByText("you have $19")).toBeTruthy();
    expect(within(sheet()).getByText("10")).toBeTruthy();
    expect(within(sheet()).getByText("Rivals over $19")).toBeTruthy();
  });

  it("shows no outbid box with no pick", () => {
    renderBoard();
    expect(within(sheet()).queryByText("Can outbid you")).toBeNull();
  });

  it("shows no outbid box for a drop, which has no price", () => {
    localStorage.setItem("cpc.waiver-team", "3");
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Drops" }));
    fireEvent.click(within(field()).getByRole("button", { name: "Austin Ekeler" }));
    expect(within(sheet()).queryByText("Can outbid you")).toBeNull();
  });
});

describe("the Change link", () => {
  it("opens the list again with the pick checked, and a new pick replaces the old", () => {
    localStorage.setItem("cpc.waiver-team", "3");
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Change your team" }));
    expect(chip()).toBeNull();
    const checked = within(pickList()!).getByRole("radio", { checked: true });
    expect(checked.closest("label")?.textContent).toContain("Lil Fridge");
    expect(document.activeElement).toBe(checked);
    fireEvent.click(within(pickList()!).getByRole("radio", { name: /Bo Girds/ }));
    expect(within(chip()!).getByText("Bo Girds")).toBeTruthy();
    expect(localStorage.getItem("cpc.waiver-team")).toBe("6");
  });
});

describe("the drops bucket with a pick", () => {
  function dropNames() {
    return within(field()).getAllByRole("button").map((orb) => orb.getAttribute("aria-label"));
  }

  it("lists the viewer's own drop candidates first", () => {
    localStorage.setItem("cpc.waiver-team", "6");
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Drops" }));
    expect(dropNames()).toEqual(["Darren Waller", "Austin Ekeler"]);
  });

  it("keeps the file order with no pick", () => {
    renderBoard();
    fireEvent.click(screen.getByRole("button", { name: "Drops" }));
    expect(dropNames()).toEqual(["Austin Ekeler", "Darren Waller"]);
  });
});
