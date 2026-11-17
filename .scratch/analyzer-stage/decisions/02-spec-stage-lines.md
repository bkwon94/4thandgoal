# 02: What the stage lines say, and how fast they cycle

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

During the wait, short stage lines cycle under the title, such as "Weighing the sides" and "Checking the odds". The analyze call has no stream, so a line must never say that a step is done. The spec sets the list of lines, their order, and the time each line shows. The copy follows the rules of the site: no internal names, and "manager", never "rival".

## Decision

Recorded in the spec `PRD.md`, under "The stage lines", approved by Brian on 2026-11-16. The list has 12 lines, each for 2.5 s. Line 1 is "Weighing the sides" and line 12 is "Weighing it all together". The lines between them mix true general lines from the measures of the grade with lines that name a player, a team, or a manager of the trade. After line 12 the list starts again at line 2. No line says that a step is done. A screen reader hears one message, "Grading the trade".
