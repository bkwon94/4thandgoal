/**
 * Tests for the Live names part of the layout: it reads Sleeper on a page with team names, and it makes no Sleeper call
 * on the midseason report, because the report is a record of its week.
 */
import { render, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, mock } from "bun:test";
import { stubGlobal } from "../../test/stubs";
import { LiveNamesPart } from "./live-names-part";

const TEAMS = [{ rosterId: 5, names: ["Puka Deez..."], avatarUrl: null }];
const fetch = mock(async () => Response.json([]));

beforeEach(() => {
  sessionStorage.clear();
  fetch.mockClear();
  stubGlobal("fetch", fetch);
});

describe("LiveNamesPart", () => {
  it("reads the rosters and the users of the league on a week page", async () => {
    window.history.replaceState(null, "", "/2026/week-10/");
    render(<LiveNamesPart leagueId="1386167364424318976" teams={TEAMS} />);
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
  });

  it("makes no Sleeper call on the midseason report", async () => {
    window.history.replaceState(null, "", "/midseason/2026/");
    render(<LiveNamesPart leagueId="1386167364424318976" teams={TEAMS} />);
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(fetch).not.toHaveBeenCalled();
  });

  it("makes no call for a client with no league id", async () => {
    window.history.replaceState(null, "", "/2026/week-10/");
    render(<LiveNamesPart leagueId={null} teams={TEAMS} />);
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(fetch).not.toHaveBeenCalled();
  });
});
