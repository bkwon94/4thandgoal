# Power rankings: the site half

Status: ready-for-agent
Date: 2026-10-22

The spec lives in the pipeline repo at
`.scratch/rankings/pipeline/PRD.md`. Read it first. The
site tickets in this folder cover the reader for the season file, the `/rankings` route, the
expandable blurb row, the phone layout at 390, and the home page chapter below Tools.

The site reader and its fixture ship before the pipeline writes the file. The reader checks the
schema version and throws on a mismatch. A missing file hides the home chapter and shows an empty
state on the route.
