# 05: How a hunt is sent and recorded

Map: `.scratch/easter-eggs/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Decide where a manager sends an egg code: a direct message to Brian or the group chat. Decide the file and the format in which Brian records each hunter, and when the egg board shows it. Decide how a tie is settled. Brian is a manager of the league and sees each code, so decide if Brian can hunt.

## Decision

Brian decided in the grill of 2026-11-06. A manager claims an egg in a form on the site, not by a message to Brian. The form asks for the manager at each claim, with no login, no PIN, and no `localStorage`. Brian trusts the league, and a claim for a rival only helps the rival. The API logs each claim with its time and its browser, and Brian can undo a claim. The unique egg id in the claims table settles a tie: the first write wins. Brian cannot hunt, because he places every spot, so the form omits his team.
