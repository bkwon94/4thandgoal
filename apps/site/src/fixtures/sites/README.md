# Fixed site data of the tests

This folder holds a fixed copy of the published JSON files of two clients. The tests read it in place of `public/` and
`clients/<slug>/published/`.

- `cpc/public/2026/` holds weeks 6 to 8 and the season files `managers.json`, `rankings.json`, `midseason.json`, and `sim.json`.
- `norcal/public/2026/` holds week 8 and the same season files.

Each `<slug>/` folder stands for the site folder after the client build of that client, with the JSON files only. The
images stay out, because no test reads them. `src/fixtures/sites.ts` gives the paths.

The weekly publish writes only `clients/<slug>/published/`. It does not change this folder, so a new week never breaks a
test. The tests expect week 8 to be the latest week.

To change this copy, copy the JSON files from `clients/<slug>/published/` by hand. Then update the tests that read them.
