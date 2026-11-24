/**
 * Tests for the LiveNames part: a renamed team swaps in a name slot and in text, an unchanged team keeps its name, a
 * failed or slow call keeps the published names, the cache serves a second page, and a changed avatar waits for its load.
 */
import { fireEvent, render, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, mock, setSystemTime, spyOn } from "bun:test";
import { LiveNames, type PublishedTeam } from "./live-names";

const LEAGUE = "1386167364424318976";
const NEW_AVATAR = "https://sleepercdn.com/uploads/new-3.jpg";

// The published teams of cpc week 10: roster 5 is "Puka Deez...", and Sleeper now calls it "Teez Nuts".
const TEAMS: PublishedTeam[] = [
  { rosterId: 1, names: ["The Blue Tent"], avatarUrl: "https://sleepercdn.com/uploads/blue.jpg" },
  { rosterId: 3, names: ["Lil Fridge"], avatarUrl: "https://sleepercdn.com/avatars/thumbs/fridge" },
  { rosterId: 5, names: ["Puka Deez..."], avatarUrl: "https://sleepercdn.com/uploads/puka.jpg" },
];

// The two Sleeper answers, in the shape of /rosters and /users.
const ROSTERS = [
  { roster_id: 1, owner_id: "u1" },
  { roster_id: 3, owner_id: "u3" },
  { roster_id: 5, owner_id: "u5" },
];
function users(avatar3 = "https://sleepercdn.com/avatars/thumbs/fridge") {
  return [
    {
      user_id: "u1",
      display_name: "tj",
      avatar: null,
      metadata: { team_name: "The Blue Tent", avatar: "https://sleepercdn.com/uploads/blue.jpg" },
    },
    {
      user_id: "u3",
      display_name: "fridge",
      avatar: "fridge",
      metadata: avatar3.includes("thumbs")
        ? { team_name: "Lil Fridge" }
        : { team_name: "Lil Fridge", avatar: avatar3 },
    },
    {
      user_id: "u5",
      display_name: "puka",
      avatar: null,
      metadata: { team_name: "Teez Nuts ", avatar: "https://sleepercdn.com/uploads/puka.jpg" },
    },
  ];
}

/* A fetch that answers the two Sleeper calls. */
function sleeper(userList = users()) {
  return mock(async (url: string | URL | Request) => {
    const href = String(url);
    if (href === `https://api.sleeper.app/v1/league/${LEAGUE}/rosters`)
      return Response.json(ROSTERS);
    if (href === `https://api.sleeper.app/v1/league/${LEAGUE}/users`)
      return Response.json(userList);
    throw new Error(`unexpected call ${href}`);
  });
}

function page(on = true, waitMs?: number) {
  return render(
    <div>
      <h2 data-testid="slot">Puka Deez...</h2>
      <p data-testid="blurb">Puka Deez... beat Lil Fridge by 12 points.</p>
      <span data-testid="other">The Blue Tent</span>
      <img data-testid="avatar3" alt="" src="/2026/week-10/avatars/3.jpg" />
      <LiveNames leagueId={LEAGUE} teams={TEAMS} on={on} waitMs={waitMs} />
    </div>,
  );
}

beforeEach(() => {
  sessionStorage.clear();
  setSystemTime();
});

describe("LiveNames", () => {
  it("swaps a renamed team in a name slot and in text, and keeps an unchanged team", async () => {
    const fetch = sleeper();
    spyOn(globalThis, "fetch").mockImplementation(fetch as unknown as typeof globalThis.fetch);
    const { getByTestId } = page();
    // The published name shows first.
    expect(getByTestId("slot").textContent).toBe("Puka Deez...");
    await waitFor(() => expect(getByTestId("slot").textContent).toBe("Teez Nuts"));
    expect(getByTestId("blurb").textContent).toBe("Teez Nuts beat Lil Fridge by 12 points.");
    expect(getByTestId("other").textContent).toBe("The Blue Tent");
    expect(document.body.textContent).not.toContain("Puka Deez...");
    // Only the rosters and the users of the league, and no other Sleeper call.
    expect(fetch.mock.calls.map(([url]) => String(url)).sort()).toEqual([
      `https://api.sleeper.app/v1/league/${LEAGUE}/rosters`,
      `https://api.sleeper.app/v1/league/${LEAGUE}/users`,
    ]);
  });

  it("swaps an old name that a later render writes again", async () => {
    spyOn(globalThis, "fetch").mockImplementation(sleeper() as unknown as typeof globalThis.fetch);
    const { getByTestId } = page();
    await waitFor(() => expect(getByTestId("slot").textContent).toBe("Teez Nuts"));
    getByTestId("blurb").appendChild(document.createTextNode(" Puka Deez... leads."));
    await waitFor(() => expect(getByTestId("blurb").textContent).toContain("Teez Nuts leads."));
  });

  it("keeps the published names with no error when both calls fail", async () => {
    const fetch = mock(async () => {
      throw new TypeError("Failed to fetch");
    });
    spyOn(globalThis, "fetch").mockImplementation(fetch as unknown as typeof globalThis.fetch);
    const { getByTestId } = page();
    await waitFor(() => expect(fetch).toHaveBeenCalled());
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(getByTestId("slot").textContent).toBe("Puka Deez...");
    expect(sessionStorage.length).toBe(0);
  });

  it("keeps the published names when Sleeper waits past the limit", async () => {
    let aborted = false;
    spyOn(globalThis, "fetch").mockImplementation(
      ((_url: string, init?: RequestInit) =>
        new Promise((_resolve, reject) => {
          init?.signal?.addEventListener("abort", () => {
            aborted = true;
            reject(new DOMException("timed out", "AbortError"));
          });
        })) as unknown as typeof globalThis.fetch,
    );
    const { getByTestId } = page(true, 30);
    await waitFor(() => expect(aborted).toBe(true));
    expect(getByTestId("slot").textContent).toBe("Puka Deez...");
  });

  it("serves a second page from the cache for 5 minutes, then calls Sleeper again", async () => {
    const fetch = sleeper();
    spyOn(globalThis, "fetch").mockImplementation(fetch as unknown as typeof globalThis.fetch);
    setSystemTime(new Date("2026-11-25T12:00:00Z"));
    const first = page();
    await waitFor(() => expect(first.getByTestId("slot").textContent).toBe("Teez Nuts"));
    first.unmount();
    expect(fetch).toHaveBeenCalledTimes(2);

    setSystemTime(new Date("2026-11-25T12:04:59Z"));
    const second = page();
    await waitFor(() => expect(second.getByTestId("slot").textContent).toBe("Teez Nuts"));
    second.unmount();
    expect(fetch).toHaveBeenCalledTimes(2);

    setSystemTime(new Date("2026-11-25T12:05:01Z"));
    page();
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(4));
  });

  it("makes no call when it is off", async () => {
    const fetch = sleeper();
    spyOn(globalThis, "fetch").mockImplementation(fetch as unknown as typeof globalThis.fetch);
    const { getByTestId } = page(false);
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(fetch).not.toHaveBeenCalled();
    expect(getByTestId("slot").textContent).toBe("Puka Deez...");
  });

  it("shows a changed avatar from Sleeper only after it loads", async () => {
    spyOn(globalThis, "fetch").mockImplementation(
      sleeper(users(NEW_AVATAR)) as unknown as typeof globalThis.fetch,
    );
    const { getByTestId } = page();
    const local = getByTestId("avatar3") as HTMLImageElement;
    let preload: HTMLImageElement | null = null;
    await waitFor(() => {
      preload = document.querySelector(`img[data-live-avatar][src="${NEW_AVATAR}"]`);
      expect(preload).not.toBeNull();
    });
    // The local image stays until the new one loads.
    expect(local.getAttribute("src")).toBe("/2026/week-10/avatars/3.jpg");
    fireEvent.load(preload!);
    await waitFor(() => expect(local.getAttribute("src")).toBe(NEW_AVATAR));
  });
});
