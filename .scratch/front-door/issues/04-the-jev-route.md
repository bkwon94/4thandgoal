# 04: The ask box and the Jev route

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-9, AT-10, AT-13, AT-14, AT-15, AT-16, AT-17, AT-41, AT-52, AT-53, AT-54, AT-57.

**App:** both

**What to build:** A question typed in the ask box goes to a new ask endpoint of the API, behind the league passphrase. One Jev request answers the 7 typed questions of the spec, and code picks the route with yes above 0.7 and no below 0.3. A Topic route shows that Topic's Answer, for Your team or for the team that the question names. A miss shows the honest miss with the 3 closest Topics, and the API logs it in a store on its Fly volume. A rule break gets a calm refusal. The free answer route shows a short placeholder line until ticket 05. ADR 0031 and the glossary terms "honest miss" and "route" land here.

**Blocked by:** 02

**Status:** done

- [x] "who am i playing sunday" opens the next matchup of Lil Fridge (AT-9).
- [ ] "how's Bo Girds doing" answers with the 9-7 record of Bo Girds (AT-10).
- [x] "is CeeDee Lamb playing sunday" and "who won the league last year" get the honest miss with 3 Topics, and the dock chips hide (AT-13, AT-54).
- [x] A miss writes one log entry with the question, the team, the time, and the 3 Topics (AT-14). No file of the log is in the repo (AT-53).
- [x] The passphrase question gets a calm refusal with no Claude call, and the poem gets the honest miss (AT-15, AT-16).
- [x] No header and a wrong header both get 401, with no Jev call (AT-41). The store has no Thread and no login table (AT-57).
- [x] The live route eval of the 43 questions of decision 09 hits at least 35 of 40 (AT-17).
- [x] ADR 0031 says what goes to TypeSafe and to Anthropic, that the miss log lives on Fly, and that each entry stays 90 days (AT-52).

## Comments
- Closes with the squash merge of the spec PR.
