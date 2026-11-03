# 02: Schemas for the API responses

**What to build:** The API client parses the responses of the teams, analyze, and find calls with Zod schemas. The analyzer types come from those schemas. A wrong response fails with a clear error in the client, not in a component.

**Blocked by:** 01

**Status:** done

- [ ] Three response schemas in the schemas folder. The analyzer type file re-exports inferred types under the names in use.
- [ ] The two API fixture files parse through the schemas in a test.
- [ ] A response that fails the schema throws the client's error type with the path of the bad field.
- [ ] `pnpm typecheck` and `pnpm test` pass. `out/` has no diff against `main`.

## Comments

- 2026-10-31: merged into `main` from branch `modular-02-api-schemas`, commits 09b6469 and e6675ed. 500 tests. Two reviewers passed it after one fix pass: a wrong body now shows "The API sent an answer the site cannot read." with no retry.
