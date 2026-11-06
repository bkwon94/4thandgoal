# 08: Waivers and trades

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-15, and AT-16.

**App:** pipeline

**What to build:** The build refetches the transactions of each week. `midseason.json` holds the top 5 waiver hits and misses, the top 3 outbid, the streaming king data, and every trade with its Trade result from the lines 90, 60, and 10.

**Blocked by:** 01 and 02.

**Status:** ready-for-agent

- [x] The top hit is Ollie Gordon II at $40 to Unsolicited Dak Picks, and the top miss is Joe Mixon at $40.
- [x] The outbid list has The Blue Tent's $36 bid on Ollie Gordon II.
- [x] The trade report card lists 20 trades. The week 1 trade of Maye d'force B with U and NFC Least is a Robbery, and the week 8 trade is Too soon.
- [x] Rule tests cover a $0 add that is never a miss and a claim with no game after it.
