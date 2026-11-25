/**
 * The teams of a client in the shape of the teams route of the API, read from the raw files of its latest weekly build.
 * The analyzer tests use them, so the Stack holds the real rosters of the league and no made-up player.
 */
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

type RawRoster = { roster_id: number; owner_id: string; players: string[] | null };
type RawPlayer = { full_name?: string; position?: string; team?: string | null };
type RawUser = { user_id: string; display_name: string };
type Managers = { managers: { roster_id: number; team: { name: string } }[] };

/* One team of the teams route. It matches `Team` of the analyzer package, which a test checks with its schema. */
export type RawTeam = {
  roster_id: number;
  team: string;
  manager: string;
  avatar: null;
  players: {
    player_id: string;
    name: string;
    position: string;
    nfl_team: string;
    headshot: string;
  }[];
};

/* The folder of a client. Each test runs in apps/site, as pnpm runs each script of the site there. */
const clientDir = (client: string) => join(process.cwd(), "..", "..", "clients", client);

/* The last folder of a list of folders named by number, such as the seasons or the weeks. */
function last(dir: string, pattern: RegExp): string {
  const name = readdirSync(dir)
    .filter((entry) => pattern.test(entry))
    .sort()
    .at(-1);
  if (name === undefined) throw new Error(`no folder of ${pattern} in ${dir}`);
  return name;
}

/* The raw folder of the latest week of the latest season that has one, such as clients/cpc/data/2026/week-09/raw. */
export function latestRaw(client: string): { season: string; raw: string } {
  const data = join(clientDir(client), "data");
  const season = last(data, /^\d{4}$/);
  const week = readdirSync(join(data, season))
    .filter(
      (entry) =>
        /^week-\d{2}$/.test(entry) && existsSync(join(data, season, entry, "raw", "rosters.json")),
    )
    .sort()
    .at(-1);
  if (week === undefined) throw new Error(`no raw rosters in ${join(data, season)}`);
  return { season, raw: join(data, season, week, "raw") };
}

/* Each team of the client, with its name from the published managers file and each rostered player with a name.
   A `week` such as "week-10" reads the rosters of that week of the latest season, so a test of a recorded trade keeps
   the rosters of the week it was recorded on. No `week` reads the latest week. */
export function rawTeams(client: string, week?: string): RawTeam[] {
  const latest = latestRaw(client);
  const season = latest.season;
  const raw =
    week === undefined ? latest.raw : join(clientDir(client), "data", season, week, "raw");
  const read = <T>(path: string) => JSON.parse(readFileSync(path, "utf8")) as T;
  const rosters = read<RawRoster[]>(join(raw, "rosters.json"));
  const players = read<Record<string, RawPlayer>>(join(raw, "players.json"));
  const users = read<RawUser[]>(join(raw, "users.json"));
  const { managers } = read<Managers>(
    join(clientDir(client), "published", season, "managers.json"),
  );
  return rosters.map((roster) => ({
    roster_id: roster.roster_id,
    team:
      managers.find((m) => m.roster_id === roster.roster_id)?.team.name ??
      `Team ${roster.roster_id}`,
    manager: users.find((u) => u.user_id === roster.owner_id)?.display_name ?? "",
    avatar: null,
    players: (roster.players ?? []).flatMap((id) => {
      const p = players[id];
      return p?.full_name
        ? [
            {
              player_id: id,
              name: p.full_name,
              position: p.position ?? "",
              nfl_team: p.team ?? "FA",
              headshot: "",
            },
          ]
        : [];
    }),
  }));
}
