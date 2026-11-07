# 03: The letter rule and the drop each Tuesday

Spec: `.scratch/easter-eggs/PRD.md`. Acceptance tests AT-15, AT-16, AT-20, AT-21, AT-22, and AT-23.

**App:** pipeline

**What to build:** Each Tuesday the commissioner runs `make egg-draft`, confirms spots in `~/cpc-eggs/2026.toml`, and runs `make publish`. The publish sends the confirmed eggs to the API as its last step. The API gives each egg its letter by the public letter rule, with its guard and no repeat in one egg drop.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The drop route gives each egg the letter that the most managers need over the open egg words, ties in the order of the alphabet, and no repeat in one egg drop. An empty store drops A, C, D, E, G, and L.
- [ ] The drop route never gives the last letter that the leader of an egg word needs.
- [ ] `make egg-draft CLIENT=cpc WEEK=N` runs an agent with a prompt of the package. It writes six spots, each with a reason, marked not confirmed, and none repeats a dropped egg.
- [ ] The last step of `make publish` sends only the confirmed eggs of the week and says the count. With none, it says that no eggs dropped.
- [ ] When the API is down, the drop step warns and the publish exits 0. `make egg-drop CLIENT=cpc WEEK=N` retries.
- [ ] The publish of a client without the package skips the drop.
- [ ] The egg file sits outside the repo. A test runs on a temp copy and sends it to the API app in process.
