/**
 * The LiveNames part: it reads the Live name and the avatar of each team from Sleeper in the browser, and swaps each
 * renamed team on the page. The published names show first, and a failed or slow call keeps them (decision 07).
 */
"use client";

import { useEffect, useState } from "react";

/* One team as the build published it: its names in the season, newest first, and its newest avatar URL. */
export type PublishedTeam = { rosterId: number; names: string[]; avatarUrl: string | null };

/* One team as Sleeper shows it now. */
type LiveTeam = { name: string; avatarUrl: string | null };
type LiveTeams = Record<string, LiveTeam>;

const SLEEPER = "https://api.sleeper.app/v1/league";
// The pipeline builds the same thumb URL from the avatar id of a user.
const AVATAR_THUMB = "https://sleepercdn.com/avatars/thumbs/";
// Sleeper's CDN keeps each answer for 300 s, so a cache of the same time asks for nothing that could be newer.
const CACHE_MS = 5 * 60 * 1000;
const WAIT_MS = 3000;
// A local avatar of a week folder, such as /2026/week-10/avatars/3.jpg. The roster id is the file name.
const LOCAL_AVATAR = /\/\d{4}\/week-\d{2}\/avatars\/(\d+)\.\w+$/;

type RawRoster = { roster_id: number; owner_id: string | null };
type RawUser = {
  user_id: string;
  display_name: string;
  avatar?: string | null;
  metadata?: { team_name?: string | null; avatar?: string | null } | null;
};

const cacheKey = (leagueId: string) => `live-names:${leagueId}`;

/* The cached Live names of the league, or null when there are none or they are older than 5 minutes. */
function cached(leagueId: string): LiveTeams | null {
  try {
    const raw = sessionStorage.getItem(cacheKey(leagueId));
    if (!raw) return null;
    const entry = JSON.parse(raw) as { at: number; teams: LiveTeams };
    return Date.now() - entry.at < CACHE_MS ? entry.teams : null;
  } catch {
    return null;
  }
}

/* The team name and the avatar URL of a user, by the same rules as the pipeline, so an unchanged team reads the same. */
function liveTeam(user: RawUser): LiveTeam {
  const name = (user.metadata?.team_name || user.display_name).trim();
  const avatarUrl = user.metadata?.avatar || (user.avatar ? AVATAR_THUMB + user.avatar : null);
  return { name, avatarUrl };
}

/* The two public Sleeper calls: the rosters for the owner of each roster, and the users for each name and avatar.
   A failed call or a wait past the limit gives null, so the page keeps the published names. */
async function fetchLive(leagueId: string, waitMs: number): Promise<LiveTeams | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), waitMs);
  try {
    const get = async <T,>(path: string): Promise<T> => {
      const answer = await fetch(`${SLEEPER}/${leagueId}/${path}`, { signal: controller.signal });
      if (!answer.ok) throw new Error(`Sleeper ${path} answered ${answer.status}`);
      return (await answer.json()) as T;
    };
    const [rosters, users] = await Promise.all([
      get<RawRoster[]>("rosters"),
      get<RawUser[]>("users"),
    ]);
    const byId = new Map(users.map((user) => [user.user_id, user]));
    const teams: LiveTeams = {};
    for (const roster of rosters) {
      const user = roster.owner_id ? byId.get(roster.owner_id) : undefined;
      if (user) teams[String(roster.roster_id)] = liveTeam(user);
    }
    sessionStorage.setItem(cacheKey(leagueId), JSON.stringify({ at: Date.now(), teams }));
    return teams;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/* Each old name to swap and its Live name, longest first, so a name inside a longer name never swaps first. An old name
   that is the Live name of another team stays, because the text may mean that team. */
function nameSwaps(teams: PublishedTeam[], live: LiveTeams): [string, string][] {
  const liveNames = new Set(Object.values(live).map((team) => team.name));
  const swaps: [string, string][] = [];
  for (const team of teams) {
    const now = live[String(team.rosterId)]?.name;
    if (!now || now === team.names[0]) continue;
    for (const old of new Set(team.names)) {
      if (old && old !== now && !liveNames.has(old)) swaps.push([old, now]);
    }
  }
  return swaps.sort((a, b) => b[0].length - a[0].length);
}

/* The new avatar URL of each team whose Live avatar differs from the published one. */
function avatarSwaps(
  teams: PublishedTeam[],
  live: LiveTeams,
): Map<number, { from: string | null; to: string }> {
  const swaps = new Map<number, { from: string | null; to: string }>();
  for (const team of teams) {
    const to = live[String(team.rosterId)]?.avatarUrl;
    if (to && to !== team.avatarUrl) swaps.set(team.rosterId, { from: team.avatarUrl, to });
  }
  return swaps;
}

/* The text that this part wrote in each node. A node that still holds it needs no new swap. */
const written = new WeakMap<Node, string>();

/* Swap each full old name in each text node under the root. */
function swapText(root: Node, swaps: [string, string][]) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const text = node.nodeValue ?? "";
    if (written.get(node) === text) continue;
    const parent = node.parentElement?.tagName;
    if (parent === "SCRIPT" || parent === "STYLE") continue;
    let next = text;
    for (const [old, now] of swaps) if (next.includes(old)) next = next.split(old).join(now);
    if (next !== text) {
      written.set(node, next);
      node.nodeValue = next;
    }
  }
}

/* The roster id of an avatar image of a team, by its local path or by its published URL. */
function rosterOf(
  img: HTMLImageElement,
  avatars: Map<number, { from: string | null; to: string }>,
): number | null {
  const src = img.getAttribute("src") ?? "";
  const local = LOCAL_AVATAR.exec(new URL(src, window.location.href).pathname);
  if (local) return Number(local[1]);
  for (const [rosterId, { from }] of avatars) if (from && src === from) return rosterId;
  return null;
}

/* Point each avatar image of a team with a loaded new avatar at the new URL. */
function swapAvatars(
  root: ParentNode,
  avatars: Map<number, { from: string | null; to: string }>,
  loaded: Set<number>,
) {
  for (const img of root.querySelectorAll<HTMLImageElement>("img:not([data-live-avatar])")) {
    const rosterId = rosterOf(img, avatars);
    const swap = rosterId === null ? undefined : avatars.get(rosterId);
    if (swap && loaded.has(rosterId!) && img.getAttribute("src") !== swap.to)
      img.setAttribute("src", swap.to);
  }
}

/* The part. It renders only a hidden image for each changed avatar, so the new image loads before the page shows it.
   `on` false makes no call, such as on the midseason report. `waitMs` is the limit of the wait for Sleeper. */
export function LiveNames({
  leagueId,
  teams,
  on = true,
  waitMs = WAIT_MS,
}: {
  leagueId: string;
  teams: PublishedTeam[];
  on?: boolean;
  waitMs?: number;
}) {
  const [live, setLive] = useState<LiveTeams | null>(null);
  const [loaded, setLoaded] = useState<Set<number>>(() => new Set());

  useEffect(() => {
    if (!on || teams.length === 0) return;
    let current = true;
    const hit = cached(leagueId);
    if (hit) setLive(hit);
    else void fetchLive(leagueId, waitMs).then((answer) => current && answer && setLive(answer));
    return () => {
      current = false;
    };
  }, [leagueId, teams, on, waitMs]);

  const avatars = live
    ? avatarSwaps(teams, live)
    : new Map<number, { from: string | null; to: string }>();

  useEffect(() => {
    if (!on || !live) return;
    const swaps = nameSwaps(teams, live);
    const apply = () => {
      if (swaps.length > 0) swapText(document.body, swaps);
      if (loaded.size > 0) swapAvatars(document.body, avatarSwaps(teams, live), loaded);
    };
    apply();
    // A later render or a new page can write an old name or an old avatar again, so each change of the page swaps again.
    const observer = new MutationObserver(apply);
    observer.observe(document.body, {
      subtree: true,
      childList: true,
      characterData: true,
      attributes: true,
      attributeFilter: ["src"],
    });
    return () => observer.disconnect();
  }, [teams, live, on, loaded]);

  if (!on) return null;
  return (
    <>
      {[...avatars].map(([rosterId, { to }]) => (
        <img
          key={rosterId}
          src={to}
          alt=""
          hidden
          aria-hidden="true"
          data-live-avatar=""
          onLoad={() => setLoaded((done) => new Set(done).add(rosterId))}
        />
      ))}
    </>
  );
}
